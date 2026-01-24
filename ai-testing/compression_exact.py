"""
Exact Python translation of the C++ DCT compression code

Maintains all bit-level operations, RLE encoding, and exact algorithm
"""
import numpy as np
import cv2
import math
import struct
import os
from typing import List, Tuple

# Try to use scipy for faster DCT, fallback to manual if not available
try:
    from scipy.fftpack import dct, idct
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


# Constants
PI_D = 3.1415926535897932384626433832795


# Zigzag order for 8x8 blocks
ZZ = [
    0,  1,  8, 16,  9,  2,  3, 10,
    17, 24, 32, 25, 18, 11,  4,  5,
    12, 19, 26, 33, 40, 48, 41, 34,
    27, 20, 13,  6,  7, 14, 21, 28,
    35, 42, 49, 56, 57, 50, 43, 36,
    29, 22, 15, 23, 30, 37, 44, 51,
    58, 59, 52, 45, 38, 31, 39, 46,
    53, 60, 61, 54, 47, 55, 62, 63
]


class BitWriter:
    """Exact translation of C++ BitWriter"""
    def __init__(self):
        self.buf = bytearray()
        self.bitpos = 0
    
    def writeBit(self, b: int):
        if (self.bitpos & 7) == 0:
            self.buf.append(0)
        if b:
            self.buf[-1] |= (1 << (7 - (self.bitpos & 7)))
        self.bitpos += 1
    
    def writeBits(self, v: int, nbits: int):
        for i in range(nbits - 1, -1, -1):
            self.writeBit((v >> i) & 1)
    
    def writeSigned(self, val: int, nbits: int):
        if nbits == 32:
            mask = 0xFFFFFFFF
        else:
            mask = (1 << nbits) - 1
        twos = val & mask
        self.writeBits(twos, nbits)
    
    def alignToByte(self):
        while self.bitpos & 7:
            self.writeBit(0)


class BitReader:
    """Exact translation of C++ BitReader"""
    def __init__(self, buf: bytes):
        self.buf = buf
        self.bitpos = 0
    
    def readBit(self) -> int:
        if self.bitpos // 8 >= len(self.buf):
            raise RuntimeError("BitReader overflow")
        byte = self.buf[self.bitpos // 8]
        b = (byte >> (7 - (self.bitpos & 7))) & 1
        self.bitpos += 1
        return b
    
    def readBits(self, nbits: int) -> int:
        v = 0
        for i in range(nbits):
            v = (v << 1) | self.readBit()
        return v
    
    def readSigned(self, nbits: int) -> int:
        raw = self.readBits(nbits)
        if nbits == 32:
            return np.int32(raw)
        mask = (1 << nbits) - 1
        if raw & (1 << (nbits - 1)):
            return np.int32(raw | (~mask))
        else:
            return np.int32(raw)


def bits_for_signed(v: int) -> int:
    """Calculate bits needed for signed value"""
    if v == 0:
        return 1
    m = v if v > 0 else -v - 1
    bits = 0
    while m > 0:
        bits += 1
        m >>= 1
    return bits + 1


def fdct8x8(inp: np.ndarray) -> np.ndarray:
    """Forward DCT 8x8 - optimized version using scipy if available, else manual"""
    if SCIPY_AVAILABLE:
        # Use scipy's optimized DCT (much faster)
        # Apply 2D DCT: dct(dct(block.T, norm='ortho').T, norm='ortho')
        # This matches the C++ algorithm
        dct_result = dct(dct(inp.T, norm='ortho', axis=0).T, norm='ortho', axis=0)
        return dct_result
    else:
        # Fallback to manual implementation (slower but exact)
        out = np.zeros((8, 8), dtype=np.float64)
        for u in range(8):
            Cu = (1.0 / math.sqrt(2.0)) if u == 0 else 1.0
            for v in range(8):
                Cv = (1.0 / math.sqrt(2.0)) if v == 0 else 1.0
                # Vectorized inner loop
                x_arr = np.arange(8, dtype=np.float64)
                y_arr = np.arange(8, dtype=np.float64)
                X, Y = np.meshgrid(x_arr, y_arr, indexing='ij')
                cos_xu = np.cos(((2 * X + 1) * u * PI_D) / 16.0)
                cos_yv = np.cos(((2 * Y + 1) * v * PI_D) / 16.0)
                cos_matrix = cos_xu * cos_yv
                sum_val = np.sum(inp * cos_matrix)
                out[u, v] = 0.25 * Cu * Cv * sum_val
        return out


def idct8x8(inp: np.ndarray) -> np.ndarray:
    """Inverse DCT 8x8 - optimized version using scipy if available, else manual"""
    if SCIPY_AVAILABLE:
        # Use scipy's optimized IDCT (much faster)
        # Apply 2D IDCT: idct(idct(block.T, norm='ortho').T, norm='ortho')
        idct_result = idct(idct(inp.T, norm='ortho', axis=0).T, norm='ortho', axis=0)
        return idct_result
    else:
        # Fallback to manual implementation (slower but exact)
        out = np.zeros((8, 8), dtype=np.float64)
        for x in range(8):
            for y in range(8):
                sum_val = 0.0
                for u in range(8):
                    Cu = (1.0 / math.sqrt(2.0)) if u == 0 else 1.0
                    cos_xu = math.cos(((2 * x + 1) * u * PI_D) / 16.0)
                    for v in range(8):
                        Cv = (1.0 / math.sqrt(2.0)) if v == 0 else 1.0
                        cos_yv = math.cos(((2 * y + 1) * v * PI_D) / 16.0)
                        sum_val += Cu * Cv * inp[u, v] * cos_xu * cos_yv
                out[x, y] = 0.25 * sum_val
        return out


def apply_factor_triangular(coeffs: List[int], factor: int):
    """Triangular quantization: K(u,v)=15-(u+v)"""
    for u in range(8):
        for v in range(8):
            idx = u * 8 + v
            K = 15 - (u + v)
            if K <= factor:
                coeffs[idx] = 0


def encode_block(blk: List[int], bw: BitWriter):
    """Encode 8x8 block with RLE - exact translation"""
    # DC: 12-bit two's complement
    DC = blk[0]
    DC = max(-2040, min(2040, DC))
    bw.writeSigned(DC, 12)
    
    # AC: RLE in zigzag order
    zzblock = [blk[ZZ[i]] for i in range(64)]
    
    processedAC = 0
    i = 1
    while processedAC < 63:
        run = 0
        while i < 64 and zzblock[i] == 0:
            run += 1
            i += 1
            if processedAC + run == 63:
                # b) 0 | run(6)
                bw.writeBit(0)
                bw.writeBits(run, 6)
                processedAC += run
                run = 0
                break
        
        if processedAC == 63:
            break
        
        if run > 0:
            ac = zzblock[i]
            L = bits_for_signed(ac)
            L = max(1, min(13, L))
            # a) 0 | run(6) | len(4) | val(len)
            bw.writeBit(0)
            bw.writeBits(run, 6)
            bw.writeBits(L, 4)
            bw.writeSigned(ac, L)
            processedAC += run + 1
            i += 1
        else:
            ac = zzblock[i]
            L = bits_for_signed(ac)
            L = max(1, min(13, L))
            # c) 1 | len(4) | val(len)
            bw.writeBit(1)
            bw.writeBits(L, 4)
            bw.writeSigned(ac, L)
            processedAC += 1
            i += 1


def decode_block(br: BitReader) -> List[int]:
    """Decode 8x8 block - exact translation"""
    outblk = [0] * 64
    DC = br.readSigned(12)
    outblk[0] = DC
    
    processedAC = 0
    zpos = 1
    while processedAC < 63:
        flag = br.readBit()
        if flag == 0:
            run = br.readBits(6)
            if processedAC + run == 63:
                for r in range(run):
                    nat = ZZ[zpos]
                    zpos += 1
                    outblk[nat] = 0
                processedAC += run
            else:
                L = br.readBits(4)
                ac = br.readSigned(L)
                for r in range(run):
                    nat = ZZ[zpos]
                    zpos += 1
                    outblk[nat] = 0
                nat = ZZ[zpos]
                zpos += 1
                outblk[nat] = ac
                processedAC += run + 1
        else:
            L = br.readBits(4)
            ac = br.readSigned(L)
            nat = ZZ[zpos]
            zpos += 1
            outblk[nat] = ac
            processedAC += 1
    
    return outblk


def clampi(v: int, lo: int, hi: int) -> int:
    """Clamp integer value"""
    return lo if v < lo else (hi if v > hi else v)


def write_u16le(buf: bytearray, v: int):
    """Write 16-bit little-endian"""
    buf.append(v & 0xFF)
    buf.append((v >> 8) & 0xFF)


def read_u16le(buf: bytes, off: int) -> Tuple[int, int]:
    """Read 16-bit little-endian"""
    if off + 2 > len(buf):
        raise RuntimeError("Napačna glava datoteke")
    v = buf[off] | (buf[off + 1] << 8)
    return v, off + 2


def compress_image(img_path: str, out_path: str, compression_factor: int) -> dict:
    """
    Compress image - exact translation of C++ compression
    
    Args:
        img_path: Input image path
        out_path: Output .bin file path
        compression_factor: 0-15
    
    Returns:
        dict with compression statistics
    """
    # Load image
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise RuntimeError(f"Ne morem odpreti vhodne slike: {img_path}")
    
    channels = img.shape[2] if len(img.shape) == 3 else 1
    if channels != 3 and channels != 4:
        raise RuntimeError("Nepodprt število kanalov (mora biti RGB ali RGBA).")
    
    # Convert color space
    if channels == 4:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
    else:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    H, W = rgb.shape[:2]
    W8 = (W + 7) & ~7
    H8 = (H + 7) & ~7
    
    # Pad to multiple of 8
    if channels == 4:
        pad = np.zeros((H8, W8, 4), dtype=np.uint8)
    else:
        pad = np.zeros((H8, W8, 3), dtype=np.uint8)
    pad[:H, :W] = rgb
    
    # Create output buffer
    out = bytearray()
    write_u16le(out, W)
    write_u16le(out, H)
    out.append(channels)
    out.append(compression_factor)
    
    bw = BitWriter()
    
    # Process 8x8 blocks
    for by in range(0, H8, 8):
        for bx in range(0, W8, 8):
            for c in range(channels):
                # Extract block and shift to [-128, 127] - vectorized
                blk = pad[by:by+8, bx:bx+8, c].astype(np.float64) - 128.0
                
                # DCT
                dct = fdct8x8(blk)
                
                # Round and quantize - vectorized
                coeffs = np.round(dct).astype(np.int32).flatten().tolist()
                apply_factor_triangular(coeffs, compression_factor)
                
                # Encode block
                encode_block(coeffs, bw)
    
    bw.alignToByte()
    out.extend(bw.buf)
    
    # Write to file
    with open(out_path, 'wb') as f:
        f.write(out)
    
    # Statistics
    raw_size = W * H * channels
    compressed_size = len(out)
    
    return {
        'width': W,
        'height': H,
        'channels': channels,
        'factor': compression_factor,
        'raw_bytes': raw_size,
        'compressed_bytes': compressed_size,
        'ratio': raw_size / compressed_size if compressed_size > 0 else 0
    }


def decompress_image(bin_path: str, out_path: str) -> dict:
    """
    Decompress image - exact translation of C++ decompression
    
    Args:
        bin_path: Input .bin file path
        out_path: Output image path
    
    Returns:
        dict with decompression info
    """
    # Read binary file
    with open(bin_path, 'rb') as f:
        data = f.read()
    
    if len(data) < 6:
        raise RuntimeError("Pokvarjena .bin datoteka (premalo bajtov)")
    
    # Read header
    off = 0
    W, off = read_u16le(data, off)
    H, off = read_u16le(data, off)
    chans = data[off]
    off += 1
    used_factor = data[off]
    off += 1
    
    if chans != 3 and chans != 4:
        raise RuntimeError("Pričakovani 3 ali 4 kanali.")
    
    # Create bit reader
    bitbuf = data[off:]
    br = BitReader(bitbuf)
    
    W8 = (W + 7) & ~7
    H8 = (H + 7) & ~7
    
    if chans == 4:
        rec = np.zeros((H8, W8, 4), dtype=np.uint8)
    else:
        rec = np.zeros((H8, W8, 3), dtype=np.uint8)
    
    # Decode blocks
    for by in range(0, H8, 8):
        for bx in range(0, W8, 8):
            for c in range(chans):
                # Decode block
                coeffs = decode_block(br)
                
                # Convert to 2D array
                dct = np.zeros((8, 8), dtype=np.float64)
                for u in range(8):
                    for v in range(8):
                        dct[u, v] = float(coeffs[u * 8 + v])
                
                # IDCT
                blk = idct8x8(dct)
                
                # Shift back to [0, 255] and clamp
                for i in range(8):
                    for j in range(8):
                        val = int(round(blk[i, j] + 128.0))
                        val = clampi(val, 0, 255)
                        rec[by + i, bx + j, c] = val
    
    # Crop to original size
    crop = rec[:H, :W].copy()
    
    # Convert color space back
    if chans == 4:
        outB = cv2.cvtColor(crop, cv2.COLOR_RGBA2BGRA)
    else:
        outB = cv2.cvtColor(crop, cv2.COLOR_RGB2BGR)
    
    # Write output
    if not cv2.imwrite(out_path, outB):
        raise RuntimeError("Ne morem zapisati izhodne slike.")
    
    return {
        'width': W,
        'height': H,
        'channels': chans,
        'factor': used_factor
    }


def compress_yolo_frames_exact(compression_factor=8, status_callback=None):
    """
    Compress every 5th frame using exact C++ algorithm
    
    Args:
        compression_factor: 0-15 (default 8)
        status_callback: Optional callback for status updates
    
    Returns:
        tuple: (success, message, stats)
    """
    def update_status(msg):
        if status_callback:
            status_callback(msg)
        print(msg)
    
    video_path = "output/yolo_predict.mp4"
    output_dir = "output"
    
    if not os.path.exists(video_path):
        return False, f"Video not found: {video_path}", {}
    
    # Create output directories
    frames_dir = os.path.join(output_dir, "frames_extracted")
    compressed_dir = os.path.join(output_dir, "frames_compressed")
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(compressed_dir, exist_ok=True)
    
    try:
        # Open video
        update_status("Kompresija: Odpiranje videa...")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return False, f"Cannot open video: {video_path}", {}
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        update_status(f"Kompresija: Ekstrahiranje vsakega 5. frame-a ({total_frames} skupaj)...")
        
        frame_idx = 0
        extracted_count = 0
        
        # Extract every 5th frame
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % 5 == 0:
                frame_filename = os.path.join(frames_dir, f"frame_{frame_idx:06d}.png")
                cv2.imwrite(frame_filename, frame)
                extracted_count += 1
                
                if extracted_count % 20 == 0:
                    update_status(f"Kompresija: Ekstrahirano {extracted_count} frame-ov...")
            
            frame_idx += 1
        
        cap.release()
        update_status(f"Kompresija: Ekstrahirano {extracted_count} frame-ov")
        
        # Compress each frame
        update_status(f"Kompresija: Stiskanje frame-ov (faktor {compression_factor})...")
        
        compressed_count = 0
        failed_count = 0
        original_size = 0
        compressed_size = 0
        
        for filename in sorted(os.listdir(frames_dir)):
            if filename.endswith('.png'):
                input_path = os.path.join(frames_dir, filename)
                output_path = os.path.join(compressed_dir, filename.replace('.png', '.bin'))
                
                try:
                    # Compress using exact C++ algorithm
                    stats = compress_image(input_path, output_path, compression_factor)
                    
                    original_size += stats['raw_bytes']
                    compressed_size += stats['compressed_bytes']
                    compressed_count += 1
                    
                    if compressed_count % 20 == 0:
                        update_status(f"Kompresija: Stisnjeno {compressed_count}/{extracted_count} frame-ov...")
                
                except Exception as e:
                    print(f"Error compressing {filename}: {e}")
                    failed_count += 1
        
        stats = {
            'extracted_frames': extracted_count,
            'compressed_frames': compressed_count,
            'failed_frames': failed_count,
            'original_size_mb': original_size / 1024 / 1024,
            'compressed_size_mb': compressed_size / 1024 / 1024,
            'compression_ratio': original_size / compressed_size if compressed_size > 0 else 0
        }
        
        if compressed_count > 0:
            msg = (f"Kompresija končana: {compressed_count} frame-ov stisnjenih "
                   f"({stats['compression_ratio']:.2f}x razmerje)")
            update_status(msg)
            return True, msg, stats
        else:
            return False, "Kompresija ni uspela", stats
    
    except Exception as e:
        return False, f"Napaka pri kompresiji: {str(e)}", {}


if __name__ == "__main__":
    # Test compression
    print("Testing exact C++ algorithm compression...")
    success, msg, stats = compress_yolo_frames_exact()
    
    if success:
        print(f"\n✓ {msg}")
        print(f"  Original: {stats['original_size_mb']:.2f} MB")
        print(f"  Compressed: {stats['compressed_size_mb']:.2f} MB")
        print(f"  Ratio: {stats['compression_ratio']:.2f}x")
    else:
        print(f"\n✗ {msg}")

