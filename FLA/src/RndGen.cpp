#pragma once

#include<random>

class RndGen {
    private:
        //For RNG
        time_t seed = time(NULL);

        std::mt19937_64 gen = std::mt19937_64(seed);
        std::uniform_real_distribution<double> dist =std::uniform_real_distribution<double>(0.0, 1.0);

        
    public:
        RndGen(time_t sd) {
            seed = sd; 
            gen = std::mt19937_64(seed);
        }
        double rnd() {
            return dist(gen);
        }
        double norm(double mean, double std) {
            std::normal_distribution<double> normDist(mean, std);
            return normDist(gen);
        }
};