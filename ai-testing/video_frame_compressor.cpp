#include <cstdint>
#include <cmath>
#include <vector>
#include <iostream>
#include <iomanip>
#include <stdexcept>
#include <string>
#include <limits>
#include <cstdio>
#include <algorithm>
#include <cassert>
#include <cstring>
#include <cstdlib>
#include <chrono>
#include <opencv2/opencv.hpp>

using namespace std;

struct BitWriter {
    std::vector<uint8_t> buf;
    uint32_t bitpos = 0;
    
    void writeBit(uint32_t b) {
        if ((bitpos & 7u) == 0) buf.push_back(0);
        if (b) buf.back() |= (1u << (7 - (bitpos & 7u)));
        bitpos++;
    }
    
    void writeBits(uint32_t v, int nbits) {
        for (int i = nbits - 1; i >= 0; --i) writeBit((v >> i) & 1u);
    }
    
    void writeSigned(int32_t val, int nbits) {
        uint32_t mask = (nbits == 32) ? 0xFFFFFFFFu : ((1u << nbits) - 1u);
        uint32_t twos = (uint32_t)val & mask;
        writeBits(twos, nbits);
    }
    
    void alignToByte() { while (bitpos & 7u) writeBit(0); }
};

struct BitReader {
    const std::vector<uint8_t>& buf;
    uint32_t bitpos = 0;
    
    BitReader(const std::vector<uint8_t>& b) : buf(b) {}
    
    uint32_t readBit() {
        if (bitpos / 8 >= buf.size()) throw std::runtime_error("BitReader overflow");
        uint8_t byte = buf[bitpos / 8];
        uint32_t b = (byte >> (7 - (bitpos & 7u))) & 1u;
        bitpos++;
        return b;
    }
    
    uint32_t readBits(int nbits) { 
        uint32_t v = 0; 
        for (int i = 0; i < nbits; i++) v = (v << 1) | readBit(); 
        return v; 
    }
    
    int32_t readSigned(int nbits) {
        uint32_t raw = readBits(nbits);
        if (nbits == 32) return (int32_t)raw;
        uint32_t mask = (1u << nbits) - 1u;
        if (raw & (1u << (nbits - 1))) {
            return (int32_t)(raw | (~mask));
        }
        else return (int32_t)raw;
    }
};

static inline int bits_for_signed(int v) {
    if (v == 0) return 1;
    int m = v > 0 ? v : -v - 1;
    int bits = 0; 
    while (m > 0) { bits++; m >>= 1; }
    return bits + 1;
}

static const double PI_D = 3.1415926535897932384626433832795;

void fdct8x8(const double in[8][8], double out[8][8]) {
    for (int u = 0; u < 8; ++u) {
        for (int v = 0; v < 8; ++v) {
            double Cu = (u == 0) ? (1.0 / sqrt(2.0)) : 1.0;
            double Cv = (v == 0) ? (1.0 / sqrt(2.0)) : 1.0;
            double sum = 0.0;
            for (int x = 0; x < 8; ++x)
                for (int y = 0; y < 8; ++y)
                    sum += in[x][y] *
                           cos(((2 * x + 1) * u * PI_D) / 16.0) *
                           cos(((2 * y + 1) * v * PI_D) / 16.0);
            out[u][v] = 0.25 * Cu * Cv * sum;
        }
    }
}

void idct8x8(const double in[8][8], double out[8][8]) {
    for (int x = 0; x < 8; ++x) {
        for (int y = 0; y < 8; ++y) {
            double sum = 0.0;
            for (int u = 0; u < 8; ++u) {
                for (int v = 0; v < 8; ++v) {
                    double Cu = (u == 0) ? (1.0 / sqrt(2.0)) : 1.0;
                    double Cv = (v == 0) ? (1.0 / sqrt(2.0)) : 1.0;
                    sum += Cu * Cv * in[u][v] *
                           cos(((2 * x + 1) * u * PI_D) / 16.0) *
                           cos(((2 * y + 1) * v * PI_D) / 16.0);
                }
            }
            out[x][y] = 0.25 * sum;
        }
    }
}

static const int ZZ[64] = {
     0,  1,  8, 16,  9,  2,  3, 10,
    17, 24, 32, 25, 18, 11,  4,  5,
    12, 19, 26, 33, 40, 48, 41, 34,
    27, 20, 13,  6,  7, 14, 21, 28,
    35, 42, 49, 56, 57, 50, 43, 36,
    29, 22, 15, 23, 30, 37, 44, 51,
    58, 59, 52, 45, 38, 31, 39, 46,
    53, 60, 61, 54, 47, 55, 62, 63
};

// Trikotna kvantizacija: K(u,v)=15-(u+v); postavi na 0 če je K <= faktor
void apply_factor_triangular(std::vector<int>& coeffs, int factor) {
    for (int u = 0; u < 8; ++u) {
        for (int v = 0; v < 8; ++v) {
            int idx = u * 8 + v;
            int K = 15 - (u + v);
            if (K <= factor) coeffs[idx] = 0;
        }
    }
}

void encode_block(const int blk[64], BitWriter& bw) {
    // DC: 12-bitni two's complement
    int DC = blk[0];
    DC = std::max(-2040, std::min(2040, DC));
    bw.writeSigned(DC, 12);
    
    // AC: RLE (pravila a/b/c) v cik-cak zaporedju
    uint zzblock[64];
    for (int i = 0; i < 64; i++) zzblock[i] = blk[ZZ[i]];
    
    int processedAC = 0;
    int i = 1;
    while (processedAC < 63) {
        int run = 0;
        while (i < 64 && zzblock[i] == 0) {
            run++; i++;
            if (processedAC + run == 63) {
                // b) 0 | run(6)
                bw.writeBit(0);
                bw.writeBits((uint32_t)run, 6);
                processedAC += run;
                run = 0;
                break;
            }
        }
        if (processedAC == 63) break;
        
        if (run > 0) {
            int ac = zzblock[i];
            int L = bits_for_signed(ac);
            L = std::max(1, std::min(13, L));
            // a) 0 | run(6) | len(4) | val(len)
            bw.writeBit(0);
            bw.writeBits((uint32_t)run, 6);
            bw.writeBits((uint32_t)L, 4);
            bw.writeSigned(ac, L);
            processedAC += run + 1;
            i++;
        }
        else {
            int ac = zzblock[i];
            int L = bits_for_signed(ac);
            L = std::max(1, std::min(13, L));
            // c) 1 | len(4) | val(len)
            bw.writeBit(1);
            bw.writeBits((uint32_t)L, 4);
            bw.writeSigned(ac, L);
            processedAC += 1;
            i++;
        }
    }
}

void decode_block(BitReader& br, int outblk[64]) {
    int DC = br.readSigned(12);
    outblk[0] = DC;
    for (int k = 1; k < 64; k++) outblk[k] = 0;
    
    int processedAC = 0;
    int zpos = 1;
    while (processedAC < 63) {
        uint32_t flag = br.readBit();
        if (flag == 0) {
            uint32_t run = br.readBits(6);
            if (processedAC + (int)run == 63) {
                for (uint32_t r = 0; r < run; ++r) {
                    int nat = ZZ[zpos++];
                    outblk[nat] = 0;
                }
                processedAC += run;
            }
            else {
                uint32_t L = br.readBits(4);
                int ac = br.readSigned((int)L);
                for (uint32_t r = 0; r < run; ++r) {
                    int nat = ZZ[zpos++];
                    outblk[nat] = 0;
                }
                int nat = ZZ[zpos++];
                outblk[nat] = ac;
                processedAC += run + 1;
            }
        }
        else {
            uint32_t L = br.readBits(4);
            int ac = br.readSigned((int)L);
            int nat = ZZ[zpos++];
            outblk[nat] = ac;
            processedAC += 1;
        }
    }
}

static inline int clampi(int v, int lo, int hi) { 
    return v < lo ? lo : (v > hi ? hi : v); 
}

void write_u16le(std::vector<uint8_t>& b, uint16_t v) {
    b.push_back(uint8_t(v & 0xFF));
    b.push_back(uint8_t((v >> 8) & 0xFF));
}

uint16_t read_u16le(const std::vector<uint8_t>& b, size_t& off) {
    if (off + 2 > b.size()) throw std::runtime_error("Napačna glava datoteke");
    uint16_t v = b[off] | (uint16_t(b[off + 1]) << 8);
    off += 2;
    return v;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    try {
        cout << "Način delovanja? (c = kompresija, d = dekompresija): ";
        char mode;
        if (!(cin >> mode)) throw std::runtime_error("Ne morem prebrati načina delovanja.");
        cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        
        if (mode == 'c' || mode == 'C') {
            std::string inPath, outBin;
            int compressionFactor;
            
            cout << "Vhodna slika (.bmp/.jpg/.png, >=500x500): ";
            std::getline(cin, inPath);
            cout << "Izhodna .bin datoteka: ";
            std::getline(cin, outBin);
            cout << "Faktor stiskanja (0-15, priporočeno: 0, 8, 14): ";
            if (!(cin >> compressionFactor)) throw std::runtime_error("Ne morem prebrati faktorja stiskanja.");
            
            if (compressionFactor < 0 || compressionFactor > 15) {
                throw std::runtime_error("Faktor stiskanja mora biti med 0 in 15.");
            }
            
            auto t_total0 = std::chrono::high_resolution_clock::now();
            
            // Naložimo sliko (UNCHANGED) in obdelamo 3/4 kanale
            cv::Mat img = cv::imread(inPath, cv::IMREAD_UNCHANGED);
            if (img.empty()) throw std::runtime_error("Ne morem odpreti vhodne slike.");
            
            int channels = img.channels();
            if (channels != 3 && channels != 4) {
                throw std::runtime_error("Nepodprt število kanalov (mora biti RGB ali RGBA).");
            }
            
            // Preverjanje velikosti slike (>=500x500)
            if (img.cols < 500 || img.rows < 500) {
                cerr << "[OPOZORILO] Slika je manjša od 500x500 pikslov (navodila zahtevajo >=500x500).\n";
                cout << "Želite vseeno nadaljevati? (d/n): ";
                char cont;
                cin >> cont;
                if (cont != 'd' && cont != 'D') {
                    cout << "Kompresija preklicana.\n";
                    return 0;
                }
            }
            
            cv::Mat rgb;
            if (channels == 4) {
                cv::cvtColor(img, rgb, cv::COLOR_BGRA2RGBA);
            }
            else {
                cv::cvtColor(img, rgb, cv::COLOR_BGR2RGB);
            }
            
            int W = rgb.cols, H = rgb.rows;
            int W8 = (W + 7) & ~7, H8 = (H + 7) & ~7;
            cv::Mat pad(H8, W8, (channels == 4 ? CV_8UC4 : CV_8UC3), cv::Scalar(0, 0, 0, 0));
            rgb.copyTo(pad(cv::Rect(0, 0, W, H)));
            
            std::vector<uint8_t> out;
            write_u16le(out, (uint16_t)W);
            write_u16le(out, (uint16_t)H);
            out.push_back((uint8_t)channels);
            out.push_back((uint8_t)compressionFactor); // Shranimo faktor za referenco
            
            BitWriter bw;
            auto t_algo0 = std::chrono::high_resolution_clock::now();
            
            // Bloki 8x8, po kanalih
            for (int by = 0; by < H8; by += 8) {
                for (int bx = 0; bx < W8; bx += 8) {
                    for (int c = 0; c < channels; c++) {
                        // Odštejemo 128 (premik iz [0,255] v [-128,127])
                        double blk[8][8];
                        if (channels == 3) {
                            for (int i = 0; i < 8; i++)
                                for (int j = 0; j < 8; j++)
                                    blk[i][j] = int(pad.at<cv::Vec3b>(by + i, bx + j)[c]) - 128;
                        }
                        else {
                            for (int i = 0; i < 8; i++)
                                for (int j = 0; j < 8; j++)
                                    blk[i][j] = int(pad.at<cv::Vec4b>(by + i, bx + j)[c]) - 128;
                        }
                        
                        double dct[8][8];
                        fdct8x8(blk, dct);
                        
                        // Zaokrožimo na celo število, uporabimo trikotni faktor
                        std::vector<int> coeffs(64);
                        for (int u = 0; u < 8; u++)
                            for (int v = 0; v < 8; v++)
                                coeffs[u * 8 + v] = (int)llround(dct[u][v]);
                        
                        apply_factor_triangular(coeffs, compressionFactor);
                        
                        // Kodiramo blok (enkoder interno uporabi cik-cak)
                        encode_block(coeffs.data(), bw);
                    }
                }
            }
            
            bw.alignToByte();
            out.insert(out.end(), bw.buf.begin(), bw.buf.end());
            
            auto t_algo1 = std::chrono::high_resolution_clock::now();
            
            FILE* f = fopen(outBin.c_str(), "wb");
            if (!f) throw std::runtime_error("Ne morem odpreti izhodne .bin datoteke");
            fwrite(out.data(), 1, out.size(), f);
            fclose(f);
            
            auto t_total1 = std::chrono::high_resolution_clock::now();
            
            uint64_t raw = (uint64_t)W * H * (uint64_t)channels;
            uint64_t comp = out.size();
            auto algo_ms = std::chrono::duration_cast<std::chrono::milliseconds>(t_algo1 - t_algo0).count();
            auto total_ms = std::chrono::duration_cast<std::chrono::milliseconds>(t_total1 - t_total0).count();
            
            cout << "\n=== REZULTATI KOMPRESIJE ===\n";
            cout << "Velikost slike: " << W << "x" << H << " (" << channels << " kanali)\n";
            cout << "Faktor stiskanja uporabljen: " << compressionFactor << "\n";
            cout << "Surovi bajti: " << raw << "\n";
            cout << "Stisnjeni bajti: " << comp << "\n";
            cout << "Kompresijsko razmerje: " << fixed << setprecision(3) << (double)raw / (double)comp << "x\n";
            cout << "Čas algoritma kompresije: " << algo_ms << " ms\n";
            cout << "Skupni čas kompresije: " << total_ms << " ms\n";
            cout << "Datoteka shranjena: " << outBin << "\n";
        }
        else if (mode == 'd' || mode == 'D') {
            std::string inBin, outImg;
            
            cout << "Vhodna .bin datoteka: ";
            std::getline(cin, inBin);
            cout << "Izhodna slika (.png/.bmp/.jpg): ";
            std::getline(cin, outImg);
            
            auto t_total0 = std::chrono::high_resolution_clock::now();
            
            std::vector<uint8_t> data;
            {
                FILE* f = fopen(inBin.c_str(), "rb");
                if (!f) throw std::runtime_error("Ne morem odpreti .bin datoteke");
                fseek(f, 0, SEEK_END); long sz = ftell(f); fseek(f, 0, SEEK_SET);
                data.resize(sz); if (sz > 0) fread(data.data(), 1, sz, f);
                fclose(f);
            }
            
            if (data.size() < 6) throw std::runtime_error("Pokvarjena .bin datoteka (premalo bajtov)");
            
            size_t off = 0;
            uint16_t W = read_u16le(data, off);
            uint16_t H = read_u16le(data, off);
            uint8_t chans = data[off++];
            uint8_t usedFactor = data[off++]; // Preberemo faktor (za informacijo)
            
            if (chans != 3 && chans != 4) throw std::runtime_error("Pričakovani 3 ali 4 kanali.");
            
            std::vector<uint8_t> bitbuf(data.begin() + off, data.end());
            BitReader br(bitbuf);
            
            int W8 = (W + 7) & ~7, H8 = (H + 7) & ~7;
            cv::Mat rec(H8, W8, (chans == 4 ? CV_8UC4 : CV_8UC3), cv::Scalar(0, 0, 0, 0));
            
            auto t_algo0 = std::chrono::high_resolution_clock::now();
            
            for (int by = 0; by < H8; by += 8) {
                for (int bx = 0; bx < W8; bx += 8) {
                    for (int c = 0; c < chans; c++) {
                        int coeffs[64];
                        decode_block(br, coeffs);
                        
                        double dct[8][8];
                        for (int u = 0; u < 8; u++)
                            for (int v = 0; v < 8; v++)
                                dct[u][v] = (double)coeffs[u * 8 + v];
                        
                        double blk[8][8];
                        idct8x8(dct, blk);
                        
                        if (chans == 3) {
                            for (int i = 0; i < 8; i++) {
                                for (int j = 0; j < 8; j++) {
                                    int val = (int)llround(blk[i][j] + 128.0);
                                    val = clampi(val, 0, 255);
                                    rec.at<cv::Vec3b>(by + i, bx + j)[c] = (uint8_t)val;
                                }
                            }
                        }
                        else {
                            for (int i = 0; i < 8; i++) {
                                for (int j = 0; j < 8; j++) {
                                    int val = (int)llround(blk[i][j] + 128.0);
                                    val = clampi(val, 0, 255);
                                    rec.at<cv::Vec4b>(by + i, bx + j)[c] = (uint8_t)val;
                                }
                            }
                        }
                    }
                }
            }
            
            cv::Mat crop = rec(cv::Rect(0, 0, W, H)).clone();
            cv::Mat outB;
            if (chans == 4) {
                cv::cvtColor(crop, outB, cv::COLOR_RGBA2BGRA);
            }
            else {
                cv::cvtColor(crop, outB, cv::COLOR_RGB2BGR);
            }
            
            auto t_algo1 = std::chrono::high_resolution_clock::now();
            
            if (!cv::imwrite(outImg, outB)) throw std::runtime_error("Ne morem zapisati izhodne slike.");
            
            auto t_total1 = std::chrono::high_resolution_clock::now();
            
            auto algo_ms = std::chrono::duration_cast<std::chrono::milliseconds>(t_algo1 - t_algo0).count();
            auto total_ms = std::chrono::duration_cast<std::chrono::milliseconds>(t_total1 - t_total0).count();
            
            cout << "\n=== REZULTATI DEKOMPRESIJE ===\n";
            cout << "Dekompresirana slika: " << outImg << "\n";
            cout << "Velikost: " << W << "x" << H << " (" << (int)chans << " kanali)\n";
            cout << "Uporabljen faktor stiskanja: " << (int)usedFactor << "\n";
            cout << "Čas algoritma dekompresije: " << algo_ms << " ms\n";
            cout << "Skupni čas dekompresije: " << total_ms << " ms\n";
        }
        else {
            throw std::runtime_error("Neznan način delovanja (uporabi 'c' ali 'd').");
        }
    }
    catch (const std::exception& e) {
        cerr << "Napaka: " << e.what() << "\n";
        return 1;
    }
    
    return 0;
}
