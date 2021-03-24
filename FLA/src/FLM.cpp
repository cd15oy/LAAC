#pragma once 

#include "SwarmUtilities.cpp"
#include "SolutionUtilities.cpp"
#include "Sample.cpp"
#include <algorithm>
#include <limits>
#include <iterator> 
#include <vector>

//Describes a Fitness landscape measure to be calculated over some sample
class FLM {
    private:
        FLM(const FLM & a);
        FLM& operator=(const FLM& other);

    public:
        FLM() {
        }

        virtual ~FLM() { 
        }

        virtual double * calculate(Sample &s) = 0;        
        virtual int lenOut() = 0;
};

class FEM : public FLM {
    private:
        bool testNeutral(Sample &s, int * symbols, double eCurrent) {
            bool allNeutral = true; //when all symbols are 0 we can stop testing es
                for(int i = 1; i < s.size(); i++) {
                    
                    double diff = s.get(i)->getFit() - s.get(i-1)->getFit();
        
                    if(diff < -eCurrent) {
                        symbols[i-1] = 2;
                        allNeutral = false;
                    } else if (diff > eCurrent) {
                        symbols[i-1] = 1;
                        allNeutral = false;
                    } else {
                        symbols[i-1] = 0;
                    }
                }
                return allNeutral;
        }
    public:
        double * calculate(Sample &s) {
            //Gives a sequence of symbols decribing the direction of change of fitness
            int symbols[s.size()-1];
            long double eCurrent = 0; //e is a threshold used to identify change 
            double eNext = 0;
            double maxFEM = 0; //entropic measure to be returned 

            long double eTop = 1.0;
            long double eBottom=0.01;
            //First, find any upper value large enough to cause all adjacet samples to be neutral
            while(!testNeutral(s, symbols, eTop))
                eTop *= 2;
            
            
            //Now we're going to lower eTop and raise eBottom to find an appropriate eCurrent in reasonable time 
            while(true) { //Need to repeatedly test different threshold values to find an appropriate threshold 
    
                eNext = eBottom + ((eTop - eBottom)/10.0); //essentially we step up eBottom by a size proportional to the current range 
                //For some functions finding the best e takes WAY to long, so we need this compromise 
                //TODO: dont forget about this weird e selection stuff

                if(fabs(eCurrent - eNext) < 0.01) break; 
                eCurrent = eNext;
                
                
                //Malan and Engelbrecht suggest incrementing by 0.05 until you find the e which causes all neutral, but this takes forever if fitness values are large, instead we use something akin to a binary search

                //generate the symbol sequence
                bool allNeutral = testNeutral(s, symbols, eCurrent);
                if(allNeutral) {
                    eTop = eCurrent;
                }else{
                    eBottom = eCurrent;
                }
                
          
                if(eTop - eBottom < 0.01) break; // we can leave once we're at most 0.01 away from the corrret e

                //count the proportion of each type of transition
                int counts[3][3];
                for(int i = 0; i < 3; i++)
                    for(int j = 0; j < 3; j++) 
                        counts[i][j] = 0;

                for(int i = 1; i < s.size()-1; i++)
                    counts[symbols[i]][symbols[i-1]] += 1;

                double FEM = 0;
                for(int i = 0; i < 3; i++) {
                    for(int j = 0; j < 3; j++) {
                        if(i == j) continue;
                        double prop = (counts[i][j] + 0.0)/s.size();
                        prop += std::numeric_limits<float>::min();
                        
                        FEM -= prop*(log(prop)/log(6));
                    }
                }

                //The recommended e to use is the one which maximizes the entropic measure, so we return the maximized measure
                if(FEM > maxFEM) maxFEM = FEM;

            }
            double * ret = new double[1]; 
            ret[0] = maxFEM;
            return ret;
        }

        int lenOut() {
            return 1;
        }
};

class M : public FLM {
    private:
        bool neutral(double * normalizedFit, int ptr) {
            double threshold = 0.00000001; //This value taken from Malan and Engelbrecht
      
            double mx = normalizedFit[ptr];
            double mn = mx; 
            for(int i = 0; i < 3; i++) {
                if(normalizedFit[ptr-i] > mx) mx = normalizedFit[ptr-i];
                if(normalizedFit[ptr-i] < mn) mn = normalizedFit[ptr-i];
            }
            if(mx - mn < threshold) 
                return true;
            else
                return false;     
        }
    public:
        double * calculate(Sample &s) {
            double normalizedFit[s.size()];  
            for(int i = 0; i < s.size(); i++) {
                normalizedFit[i] = s.get(i)->getFit();
            }
            double mx = normalizedFit[0];
            double mn = mx;
            for(int i = 0; i < s.size(); i++) {
                if(normalizedFit[i] > mx) mx = normalizedFit[i];
                if(normalizedFit[i] < mn) mn = normalizedFit[i];
            }
            for(int i = 0; i < s.size(); i++) normalizedFit[i] = (normalizedFit[i] - mn)/(mx - mn);

            int maxSeq = 0;
            int neutralCount = 0;
            int oldCount = 0;

            //We want to count the longest sequence of neutral structures
            for(int i = 2; i < s.size(); i++) {
                //if we see a neutral structure just continue
                if(neutral(normalizedFit, i)) {
                    neutralCount++;
                } else {
                    //otherwise, check how long this sequence of neural structures was, and update our count if needed
                    int len = neutralCount - oldCount;
                    if(len > maxSeq) maxSeq = len;
                    oldCount = neutralCount;
                }
            }
            //The very last structure may have been neutral, we check here 
            int len = neutralCount - oldCount;
            if(len > maxSeq) maxSeq = len;

            double * ret = new double[2];
            ret[0] = (neutralCount + 0.0)/s.size();
            ret[1] = (maxSeq + 0.0)/s.size();
            return ret;
        } 
        int lenOut() {
            return 2;
        }
};


//This estimate of mean and std-dev of gradient magnitude was described by K. Malan and A. Engelbrecht
//This was expanded based on the work of Mersmann et al (2011) and later work by Kerschke (2017), where minimum, lower quartile (25% quartile), median, mean, upper quartile (75% quartile), and maximum, and standard deviation were estimated for both the magnitude of the gradient
class Grad : public FLM {
    private:
        double mean(double * x, int start, int end) {
            double ave = 0;
            for(int i = start; i < end; i++) 
                ave += x[i];
            return ave/(end-start+0.0);
        }
        double stdDev(double * x, double ave, int start, int end) {
            double std = 0;
            for(int i = start; i < end; i++)
                std += pow(x[i] - ave, 2);
            return sqrt(std/(end-start+0.0));
        }
    
    public:
        Grad() {}

        double * calculate(Sample &s) {

            //Get the gradient estimates
            int numGrads = s.size()-1;
            double grads[numGrads];
            double lastFit = s.get(0)->getFit();
            for(int i = 1; i < s.size(); i++) {
                double curFit = s.get(i)->getFit();
                grads[i-1]= fabs(curFit - lastFit)/dist(s.get(i), s.get(i-1)); 
                lastFit = curFit;
            }

            //sort them for summary statistics 
            std::sort(grads, grads+numGrads);

            double minGrad = grads[0];
            double maxGrad = grads[numGrads-1];
            int midPoint = (int)(0.5*numGrads);
            double median = (numGrads%2 == 0)? (grads[midPoint] + grads[midPoint+1])/2.0: grads[midPoint];
            double lowerQuar = grads[(int)(numGrads*0.25)];
            double upperQuar = grads[(int)(numGrads*0.75)];

            double ave = mean(grads, 0, s.size()-1);
            double std = stdDev(grads, ave, 0, s.size()-1);

            double * ret = new double[7];
            ret[0] = minGrad;
            ret[1] = lowerQuar;
            ret[2] = median;
            ret[3] = upperQuar;
            ret[4] = maxGrad;
            ret[5] = ave;
            ret[6] = std;

            return ret;
        }

        int lenOut() {
            return 7;
        }

};

class FDC : public FLM {

    public:
    
        double * calculate(Sample &s) {
            //Get all the fitness values
            double fitVals[s.size()];
            for(int i = 0; i < s.size(); i++)
                fitVals[i] = s.get(i)->getFit();

            //Find the best fitness in the sample 
            int ptrToBest = 0;
            double bestFit = fitVals[0]; 
            for(int i = 0; i < s.size();i++)
                if(fitVals[i] < bestFit) {
                    bestFit = fitVals[i];
                    ptrToBest = i;
                }

            //Find all the distances to the best 
            double distToBest[s.size()];
            for(int i = 0; i < s.size(); i++)
                distToBest[i] = dist(s.get(i), s.get(ptrToBest));

            //find ave fit
            double aveFit = 0;
            for(int i = 0; i < s.size(); i++) aveFit += fitVals[i];
            aveFit /= s.size();

            //find ave dist to best 
            double aveDistToBest = 0;
            for(int i = 0; i < s.size(); i++) aveDistToBest += distToBest[i];
            aveDistToBest /= s.size();

            //Finally calculate FDC
            double numerator = 0;
            double denomFit = 0;
            double denomDist = 0;
            for(int i = 0; i < s.size(); i++) {
                double fitDiff = fitVals[i] - aveFit;
                double distDiff = distToBest[i] - aveDistToBest;

                numerator += (fitDiff*distDiff);
                denomFit += (fitDiff*fitDiff);
                denomDist += (distDiff*distDiff);
            }
            double * ret = new double[1];
            ret[0] = numerator/(sqrt(denomFit)*sqrt(denomDist));
            return ret;
        }

        int lenOut() {
            return 1;
        }
};

class Stag : public FLM {
    private:
        void ewma(double * x, int len, double beta) {
            for(int i = 1; i < len; i++) {
                x[i] = (beta*x[i]) + ((1-beta)*x[i-1]);
            }
        }

        double ave(double * x, int len) {
            double sum = 0;
            for(int i = 0; i < len; i++)
                sum += x[i]; 

            return (sum/=len);
        }

        double stDev(double * x, int start, int end, double ave) {
            double sum = 0;
            for(int i = start; i < end; i++) {
                sum += pow(x[i] - ave, 2);
            }
            sum /= ((end-start)-1);
            return sqrt(sum);
        }


    protected:

        double * stag(double * fit, int len) {
            double * normalizedFit = new double[len];  

            for(int i = 0; i < len; i++) {
                normalizedFit[i] = fit[i];
            }
            double mx = normalizedFit[0];
            double mn = mx;
            for(int i = 0; i < len; i++) {
                if(normalizedFit[i] > mx) mx = normalizedFit[i];
                if(normalizedFit[i] < mn) mn = normalizedFit[i];
            }
            for(int i = 0; i < len; i++) normalizedFit[i] = (normalizedFit[i] - mn)/(mx - mn);

            double lstag = 0;
            double nstag = 0;

            for(int i = 6; i < 21; i += 2) {
                double weightedAve[len];
                for(int j = 0; j < len; j++) weightedAve[j] = normalizedFit[j];
                ewma(weightedAve, len, (2.0/(i+1.0)));
                double avg = ave(weightedAve, len);
                double sd = stDev(weightedAve,0, len, avg);
                double mvingSdDev[len - (i-1)];
                for(int j = i; j <= len; j++) {
                    mvingSdDev[j-i] = stDev(weightedAve, j-i, j, avg);
                }

                double tmpnstag = 0;
                double tmplstag = 0;
                bool stuck = false;
                
                double sumRegionLen = 0;
                double numRegions = 0;
                double len = 0;

                for(int j = 0; j < len - (i-1); j++) {
                    if(stuck) {
                        if(mvingSdDev[j] < sd) {
                            len += 1.0;
                        } else {
                            stuck = false;
                            sumRegionLen += len;
                            len = 0.0;
                        }
                    } else {
                        if(mvingSdDev[j] < sd) {
                            numRegions += 1.0;
                            stuck = true;
                            len += 1.0;
                        }
                    }
                }
                if(len > 0) {
                    sumRegionLen += len;
                }
                tmplstag = sumRegionLen/numRegions;
                tmpnstag = numRegions;
                if(tmplstag > lstag) {
                    lstag = tmplstag;
                    nstag = tmpnstag;
                }
            }

            delete[] normalizedFit;
            double * ret = new double[2];
            ret[0] = lstag;
            ret[1] = nstag;

            return ret;
        }

    public:
        
        double * calculate(Sample &s) {
            double fit[s.size()];
            for(int i = 0; i < s.size(); i++)
                fit[i] = s.get(i)->getFit();
            double * ret =  stag(fit, s.size());
            return ret;
        }

        int lenOut() {
            return 2;
        }
};

class yDist: public FLM {
    protected:
        double * getVals(double * errors, int len) {
            double skew = 0;
            double kurtosis = 0; 
    
            double aveVal = 0; 

            for(int i = 0; i < len; i++) {
                aveVal += errors[i];
            }
            aveVal /= len;

            double skewNum = 0;
            double skewDenom = 0;
            double kurtNum = 0;
            double kurtDenom = 0;
            for(int i = 0; i < len; i++) {
                double diff = errors[i] - aveVal;
                
                double expDiff = diff*diff; 
                skewDenom += expDiff; 
                kurtDenom += expDiff; 

                expDiff *= diff; 
                skewNum += expDiff; 

                expDiff *= diff;
                kurtNum += expDiff; 

            }

            skewNum /= len; 
            skewDenom /= (len-1);
            skewDenom = pow(skewDenom, 3.0/2.0); 
            skew = skewNum/skewDenom; 

            kurtNum /= len;
            kurtDenom = pow(kurtDenom/len, 2);
            kurtosis = (kurtNum/kurtDenom) - 3;

            double * ret = new double[2];
            ret[0] = skew;
            ret[1] = kurtosis;

            return ret;
        }
    public:
        double * calculate(Sample &s) {
            double errors[s.size()];
            int len = s.size();
            for(int i = 0; i < len; i++)
                errors[i] = s.get(i)->getFit();
            return getVals(errors, len);
        }    

        int lenOut() {
            return 2;
        }
};

//nbc stats implemented from Kerschke P, Preuss M, Wessing S, Trautmann H (2015). “Detecting Funnel Structures by Means of Exploratory Landscape Analysis.” In Proceedings of the 17th Annual Conference on Genetic and Evolutionary Computation (GECCO), pp. 265 – 272. ACM. ISBN 978-1- 4503-3472-3. URL http://dl.acm.org/citation.cfm?doid=2739480.2754642.
//Dispersion stats implemented as described in  M. Lunacek and D. Whitley. The dispersion metric and the CMA evolution strategy. In Proceedings of the 8th Annual Conference on Genetic and Evolutionary Computation, GECCO ’06, pages 477–484. ACM, 2006
//This class calculates features based on the pairwise distance between points. Pairwise distance calculations can get very expensive if the number of samples is high, so to avoid repeated work all FLMs which require a set of pairwise distances are calculated here 
class Pairwise: public FLM {
    private:
        double percentToSample;
        int samplesToTake;
        int maxSampleSize;

        static bool compare(const std::pair<double, Solution *> & i, const std::pair<double, Solution *> & j) {
            return i.first < j.first;
        }

        double mean(double * x, int start, int end) {
            double sum = 0;
            for(int i = start; i < end; i++) {
                sum += x[i];
            }
            
            return sum/(0.0 + end - start);
        }

        double stDev(double * x, int start, int end, double ave) {
            double sum = 0;
            for(int i = start; i < end; i++) {
                sum += pow(x[i] - ave, 2);
            }
            sum /= ((end-start)-1);
            return sqrt(sum);
        }

        void summaryStats(double * orig, int len, double stats[7]) {

            double vals[len];
            for(int i = 0; i < len; i++)
                vals[i] = orig[i];
            //sort them for summary statistics 
            std::sort(vals, vals+len);

            double minGrad = vals[0];
            double maxGrad = vals[len-1];
            int midPoint = (int)(0.5*len);
            double median = (len%2 == 0)? (vals[midPoint] + vals[midPoint+1])/2.0: vals[midPoint];
            double lowerQuar = vals[(int)(len*0.25)];
            double upperQuar = vals[(int)(len*0.75)];

            double ave = mean(vals, 0, len);
            double std = stDev(vals, 0, len, ave);

            stats[0] = minGrad;
            stats[1] = lowerQuar;
            stats[2] = median;
            stats[3] = upperQuar;
            stats[4] = maxGrad;
            stats[5] = ave;
            stats[6] = std;
        }

        double cor(double * X, double * Y, int len, double aveX, double aveY) {
            double productSum = 0;
            double xSqrSum = 0;
            double ySqrSum = 0;
            for(int i = 0; i < len; i++) {
                productSum += (X[i]*Y[i]);
                xSqrSum += (X[i]*X[i]);
                ySqrSum += (Y[i]*Y[i]);
            }

            //If denominators invalid, adjust to arbitrary small value 
            //odd data/rounding errors sometimes give very small negative numbers 
            double xDenom = xSqrSum-(len*aveX*aveX);
            if(xDenom <= 0) xDenom = 0.0000000001;
            double yDenom = ySqrSum -(len*aveY*aveY);
            if(yDenom <= 0) yDenom = 0.0000000001;

            return (productSum - (len*aveX*aveY))/(sqrt(xDenom)*sqrt(yDenom));
        }

        //note that we assume the points represented by the rows/cols of dists are ordered from most fit to least fit
        void dispersionFeatures(double ** dists, int len, double stats[35]) {
            //we want to calculate dispersion for 5 sub-sets of the passed in points.
            //the sizes of these subsets will be evenly distributed among the possible sizes 
            int twentyPercent = (int)(0.2*len);
            int lenToUse = len;
            for(int i = 0; i < 5; i++) {
                int pairs = (lenToUse*(lenToUse-1))/2.0;
                double distHolder[pairs];
                int ptr = 0;
                for(int r = 0; r < lenToUse; r++)
                    for(int c = r+1; c < lenToUse; c++) {
                        distHolder[ptr] = dists[r][c];
                        ptr++;
                    }
                
                double tmpStats[7];
                summaryStats(distHolder, pairs, tmpStats);
                for(int j = 0; j < 7; j++)
                    stats[(7*i)+j] = tmpStats[j];
                lenToUse -= twentyPercent;
            }
        }

        void nearestNeighborFeatures(double ** dists, double * fits, int len, double stats[19]) {
            int nn[len]; //nearest neighbor
            int nb[len]; //nearest better

            //find the pairs of nearest neighbors and nearest betters
            for(int i = 0; i < len; i++) {
                nn[i] = (i > 0)? i-1: i+1;
                nb[i] = -1;
                for(int j = 0; j < len; j++) {
                    if(j == i) continue;
                    if(dists[i][j] < dists[i][nn[i]])
                        nn[i] = j;
                    if(fits[j] < fits[i])
                        if(nb[i] == -1 || dists[i][j] < dists[i][nb[i]])
                            nb[i] = j;
                }
            }

            //store the distances
            double nnd[len];
            double nbd[len];
            for(int i = 0; i < len; i++) {
                nnd[i] = dists[i][nn[i]];
                if(nb[i] == -1)
                    nbd[i] = 0;
                else
                    nbd[i] = dists[i][nb[i]];
            }

            //get summary stats on nearest neighbors 
            double nnStats[7];
            summaryStats(nnd, len, nnStats);
            //get summary stats on nearest betters
            double nbStats[7];
            summaryStats(nbd, len, nbStats);
            //get the nb clustering stats 
            double nbcStats[5];
            nbcStats[0] = nnStats[6]/nbStats[6];//sd(nnd)/sd(nbd)
            nbcStats[1] = nnStats[5]/nbStats[5];//mean(nnd)/mean(nbd)
            nbcStats[2] = cor(nnd, nbd, len, nnStats[5], nbStats[5]);//pearson correlation between nnd and nbd
            
            int ptr = 0;
            double qnnnb[len];
            for(int i = 0; i < len; i++)
                if(nbd[i] != 0) {
                    qnnnb[ptr] = nnd[i]/nbd[i];
                    ptr++;
                }
            

            double aveQnnnb = mean(qnnnb, 0, ptr);
            
            nbcStats[3] = stDev(qnnnb, 0, ptr, aveQnnnb);
            nbcStats[3] /= aveQnnnb; //... this what they used, no good intuitive def 

            double nbInDeg[len];
            //for each point x, count the number of other points for which x is the nearest better
            for(int i = 0; i < len; i++) 
                nbInDeg[i] = 0;
            for(int i = 0; i < len; i++)
                if(nb[i] != -1)
                    nbInDeg[nb[i]]+= 1.0;
            nbcStats[4] = -cor(nbInDeg, fits, len, mean(nbInDeg, 0, len), mean(fits, 0, len));
            //-correlation between how often a point is a nearest best, and the points fitness
            //- because fit gets better as it gets smaller
            
            for(int i = 0; i < 7; i++)
                stats[i] = nnStats[i];
            for(int i = 7; i < 14; i++)
                stats[i] = nbStats[i-7];
            for(int i = 14; i < 19; i++)
                stats[i] = nbcStats[i-14];

        }

        Pairwise(){}//Need to make sure the default constructor is inaccessible

        RndGen * rnd;

    public:
        
        //we need a RNG for the nearest better feature sampling
        Pairwise(RndGen * r) {
            rnd = r;
            percentToSample = 0.15;
            samplesToTake = 30.0;
            maxSampleSize=100;
        }

        double * calculate(Sample &s) {

            //We need to sort solutions according to fitness, without changing the order of the sample
            //std::map<double, Solution *> sorted; 
            std::vector<std::pair<double, Solution *>> sorted;

            for(int i = 0; i < s.size(); i++)
                sorted.push_back(std::pair<double, Solution *>(s.get(i)->getFit(), s.get(i))); 

            std::sort(sorted.begin(), sorted.end(), compare);

            //calculate dispersion features over the 0.15 % best
            int numBest = (int)(percentToSample*s.size());

            if(numBest <= 0) throw "Dispersion requires a larger sample";

            if(numBest > maxSampleSize) numBest = maxSampleSize;

            double ** dispPointsDist = new double*[numBest];
            for(int i = 0; i < numBest; i++)
                dispPointsDist[i] = new double[numBest];

            for(int i = 0; i < numBest; i++) {
                dispPointsDist[i][i] = 0;
                for(int j = i+1; j < numBest; j++) {
                    dispPointsDist[i][j] = dist(sorted[i].second, sorted[j].second);
                    dispPointsDist[j][i] = dispPointsDist[i][j];
                }
            }

            double dispersionStats[35];
            dispersionFeatures(dispPointsDist, numBest, dispersionStats);


            //We get away with dispersion because we only need to do pairwise distance calculations for a small group of the best solutions
            //We just can't afford to do pairwise distances for samples of 1500+ points 
            //So we're going to estimate nb features based on one or more sub-samples drawn from the provided sample



            // //First set up a main array to store all previously calculated distances 
            double ** pairwiseDist = new double *[s.size()];
            for(int i = 0; i < s.size(); i++)
                pairwiseDist[i] = new double[s.size()];

            //And an array to track which pairs have been evaluated 
            bool ** distCalculated = new bool*[s.size()];
            for(int i = 0; i < s.size(); i++) {
                distCalculated[i] = new bool[s.size()];
                for(int j = 0; j < s.size(); j++)
                    distCalculated[i][j] = false;
            }

            //add in the distances calculated for dispersion
            for(int i = 0; i < numBest; i++){
                pairwiseDist[i][i] = 0;
                for(int j = i+1; j < numBest; j++) {
                    pairwiseDist[i][j] = dispPointsDist[i][j];
                    pairwiseDist[j][i] = pairwiseDist[i][j];
                    distCalculated[i][j] = true;
                }
            }

            //now we can delete the dispersion arrays, no use anymore
            for(int i = 0; i < numBest; i++)
                delete[] dispPointsDist[i];
            delete[] dispPointsDist;

            //array to hold feature estimates
            double nbStats[19];
            for(int i = 0; i < 19; i++)
                nbStats[i] = 0;
            
            int sampleSize = (int)(percentToSample*s.size()); //for now we simply use disp sample size as the sub-sample size
            if(sampleSize > maxSampleSize) sampleSize = maxSampleSize;
            
            double ** subSampleDist = new double*[sampleSize];
            for(int i = 0; i < sampleSize; i++)
                subSampleDist[i] = new double[sampleSize];
            double fitnessValues[sampleSize];

            for(int sample = 0; sample < samplesToTake; sample ++) {
                //choose next points to sample
                int next[sampleSize];

                //choose first sampleSize elements from a random permutation to avoid duplicates
                int perm[s.size()];
                for(int i = 0; i < s.size(); i++)
                    perm[i] = i;
                for(int i = 0; i < s.size(); i++) {
                    int x = (int)(rnd->rnd()*s.size());
                    int tmp = perm[i];
                    perm[i] = perm[x];
                    perm[x] = tmp;
                }

                for(int i = 0; i < sampleSize; i++) {
                    next[i] = perm[i];
                }
                
                //calculate any missing pairwise distances
                for(int i = 0; i < sampleSize; i++) {
                    pairwiseDist[next[i]][next[i]] = 0;
                    for(int j = i+1; j < sampleSize; j++) {
                        if(distCalculated[next[i]][next[j]]) continue;
                        pairwiseDist[next[i]][next[j]] = dist(sorted[next[i]].second, sorted[next[j]].second);
                        pairwiseDist[next[j]][next[i]] = pairwiseDist[next[i]][next[j]];
                        distCalculated[next[i]][next[j]] = true;
                    }
                }

                //fill in the sub sample
                for(int i = 0; i < sampleSize; i++) {
                    fitnessValues[i] = sorted[next[i]].first;
                    for(int j = 0; j < sampleSize; j++) {
                        subSampleDist[i][j] = pairwiseDist[next[i]][next[j]];
                        
                    }
                }
                double nbStatsTmp[19];
                //Calculate nearest neighbor features over the sub-sample
                nearestNeighborFeatures(subSampleDist, fitnessValues, sampleSize, nbStatsTmp);

                for(int i = 0; i < 19; i++)
                    nbStats[i] += nbStatsTmp[i];
            }

            double * ret = new double[54];
            for(int i = 0; i < 19; i++)
                ret[i] = nbStats[i]/samplesToTake;

            for(int i = 19; i < 54; i++)
                ret[i] = dispersionStats[i-19];

            for(int i = 0; i < s.size(); i++)
                delete[] pairwiseDist[i];
            delete[] pairwiseDist;

            for(int i = 0; i < s.size(); i++)
                delete[] distCalculated[i];
            delete[] distCalculated;

            for(int i = 0; i < sampleSize; i++)
                delete[] subSampleDist[i];
            delete[] subSampleDist;

            return ret;
           
        }   

        int lenOut() {
            return 54;
        }

        void setSamplesToTake(int i) {
            samplesToTake = i;
        }

        void setPercentToSample(double i) {
            percentToSample = i;
        }
};

//Behavior TODOS:  calculate DRoC externally 
// tendency to continue in the same direction, distribution of particles (are particles clumped together in a few groups, distributed evenly over some spaces, something else?) etc

//This class represents methods of characterizing a sample for which checkpointing is not applicable
//ie a NonCheckpointableFLM involves calculating some value for EVERY iteration, rather than numeric measure(s) covering all iterations 
//Throws an exception if an implementation fails to produce properly sized output
class NonCheckpointableFLM : public FLM {
    private:
        NonCheckpointableFLM(){};
    
    protected:
        int requiredLength;
        int frequency;
        int currentLength;
        int outputSize;
        int returnedLength;

    public:
        //len is the expected length of samples to be evaluated 
        //the measure will only be computed when the required length is met
        //frequency describes how often the measure should be calculated
        //frequency = 1, means every iteration, frequency=10 means every 10th iteration
        NonCheckpointableFLM(int len, int freq) {
            requiredLength = len;
            frequency = freq;
            currentLength = requiredLength;
            outputSize = requiredLength/frequency;
            if(requiredLength % frequency != 0) outputSize++;
            returnedLength = -1;
        }

        int lenOut() {
            if(currentLength != requiredLength)
                return 0;
            else
                return outputSize;
        }

        virtual double * nonCheckpointedCalculate(Sample &s) = 0;

        double * calculate(Sample &s) {
            if(s.size() != requiredLength) {
                currentLength = 0;
                return new double[0];
            } else {
                currentLength = requiredLength;
                double * ret =  nonCheckpointedCalculate(s);
                if(returnedLength != outputSize) throw "nonCheckpointedCalculate did not produce the required number of outputs.";
                return ret;
            }
        }
};

//Gets diversity for each solution in the sample
//Throws exception if a swarm cannot be extracted from the Solution
class Diversity : public NonCheckpointableFLM {
    private:
        double diversity(Solution ** sols, int len) {
            int dims = sols[0]->numDim();

            //Get centre position
            double aveArr[dims];
            for(int i = 0; i < dims; i++)
                aveArr[i] = 0; 
            for(int r = 0; r < len; r++)
                for(int c = 0; c < dims; c++)
                    aveArr[c] += sols[r]->get(c); 

            for(int i = 0; i < dims; i++)
                aveArr[i] /= len;

            Solution ave(aveArr, dims);
            //Get ave dist from centre
            double diversity = 0; 
            for(int i = 0; i < len; i++)
                diversity += dist(&ave, sols[i]);

            return diversity/len;

        }

    public:
        Diversity(int sampleSize, int freq): NonCheckpointableFLM(sampleSize, freq) {
            
        }

        double * nonCheckpointedCalculate(Sample &s) {

            //Here we calculate diversity for each iteration
            double * ret = new double[outputSize];
            
            int valuesProduced = 0;
            for(int i = 0; i < s.size(); i++) {
                if(i%frequency == 0) {
                    int swarmSize = getSwarmSize(s.get(i));
                    Solution ** sols = getSwarm(s.get(i));
                    ret[i/frequency] = diversity(sols, swarmSize);
                    valuesProduced++;
                }
            }
            returnedLength = valuesProduced;
            return ret;
        }
};


//Step size of gBest for each iteration
class GBestStep : public NonCheckpointableFLM {
    public:
        GBestStep(int sampleSize, int freq) : NonCheckpointableFLM(sampleSize, freq) {
            outputSize = (sampleSize-1)/frequency;
            if((sampleSize-1) % frequency != 0) outputSize++;
        }

        double * nonCheckpointedCalculate(Sample &s) {
            double * ret = new double[outputSize];
            double valuesProduced = 0;
            for(int i = 1; i < s.size(); i++) {
                if((i-1)%frequency == 0) {
                    ret[(i-1)/frequency] = dist(s.get(i-1), s.get(i));
                    valuesProduced++;
                }
            }
            returnedLength = valuesProduced;

            return ret;
        }
};

//Step size for each particle for each iteration
//Throws exception if a swarm cannot be extracted from the Solution
class SwarmStep : public NonCheckpointableFLM {
    public:
        SwarmStep(int sampleSize, int swarmSize, int freq) :  NonCheckpointableFLM(sampleSize, freq) {
            outputSize = ((sampleSize-1)/frequency)*swarmSize;
            if( (sampleSize-1)% frequency != 0) outputSize+=swarmSize;

        }

        double * nonCheckpointedCalculate(Sample &s) {
            //TODO: remember that we assume that swarm size does not change
            int swarmSize = getSwarmSize(s.get(0)); //we assume that swarm size does not change
            
            int producedValues = 0;
            double * ret = new double[outputSize];
            
            Solution ** prev; 
            Solution ** cur;
            for(int i = 1; i < s.size(); i++) {
                if((i-1)%frequency == 0) {
                    prev = getSwarm(s.get(i-1));
                    cur = getSwarm(s.get(i));
                    for(int j = 0; j < swarmSize; j++) {
                        ret[((((i-1)/frequency)*swarmSize)+j)] = dist(cur[j], prev[j]);
                        producedValues++;
                    } 
                }
            }

            returnedLength = producedValues;
            prev = NULL;
            cur = NULL;

            return ret;
        }
};

//TODO: applying FLMs to problem dimensions is the same process for all FLMS
//abstract out the repeated logic 

//yDist of each dimension of gBest
class GBestyDist : public yDist {
    private:
        int length = 0;
        GBestyDist() {}
    public:
        GBestyDist(int dims) {
            length = dims;
        }
        double * calculate(Sample &s) {
            length = s.get(0)->numDim();
            double * ret = new double[2*length];
            
            double positions[s.size()];
            for(int i = 0; i < length; i++) {
                for(int j = 0; j < s.size(); j++)
                    positions[j] = s.get(j)->get(i);

                double * tmp = getVals(positions, s.size());
                ret[2*i] = tmp[0];
                ret[(2*i)+1] = tmp[1];
                delete[] tmp;
            }
            return ret;
        }

        int lenOut() {
            return 2*length;
        }
};

//yDist of each dimension of each member of the swarm 
//Throws exception if a swarm cannot be extracted from the Solution
class SwarmyDist : public yDist {
    private:
        int length = 0;
        int swarmSize;
        SwarmyDist() {}
    public:
        SwarmyDist(int dims, int swrmSz) {
            length = dims;
            swarmSize = swrmSz;
        }

        double * calculate(Sample &s) {
            length = s.get(0)->numDim();
            swarmSize = getSwarmSize(s.get(0)); //TODO: remember that we assume constant swarm size
            double * ret = new double[2*length*swarmSize];
            
            for(int p = 0; p < swarmSize; p++){
                double positions[s.size()];
                for(int i = 0; i < length; i++) {
                    for(int j = 0; j < s.size(); j++) {
                        Solution * sol = getSwarm(s.get(j))[p];
                        positions[j] = sol->get(i);
                    }

                    double * tmp = getVals(positions, s.size());
                    ret[(2*p*length) + (2*i)] = tmp[0];
                    ret[(2*p*length) + ((2*i)+1)] = tmp[1];
                    delete[] tmp;
                }
            }
            return ret;
        }

        int lenOut() {
            return 2*length*swarmSize;
        }
};


//Stag of each dimension of gBest
class GBestStag : public Stag {
    private:
        int length = 0;
        GBestStag() {}
    public:
        GBestStag(int dims) {
            length = dims;
        }

        double * calculate(Sample &s) {
            length = s.get(0)->numDim();
            double * ret = new double[2*length];
            
            double positions[s.size()];
            for(int i = 0; i < length; i++) {
                for(int j = 0; j < s.size(); j++)
                    positions[j] = s.get(j)->get(i);

                
                double * tmp = stag(positions, s.size());
                ret[2*i] = tmp[0];
                ret[(2*i)+1] = tmp[1];
                delete[] tmp;
            }
            return ret;
        }

        int lenOut() {
            return 2*length;
        }
};

//Stag of each dimension of each member of the swarm 
//Throws exception if a swarm cannot be extracted from the Solution
class SwarmStag : public Stag {
    private:
        int length;
        int swarmSize;
        SwarmStag() {}
    public:
        SwarmStag(int dims, int swrmSz) {
            length = dims;
            swarmSize = swrmSz;
        }

        double * calculate(Sample &s) {
            length = s.get(0)->numDim();
            swarmSize = getSwarmSize(s.get(0)); //TODO: remember that we assume constant swarm size
            double * ret = new double[2*length*swarmSize];
            
            int cntr = 0;
            for(int p = 0; p < swarmSize; p++){
                double positions[s.size()];
                for(int i = 0; i < length; i++) {
                    for(int j = 0; j < s.size(); j++) {
                        Solution * sol = getSwarm(s.get(j))[p];
                        positions[j] = sol->get(i);
                    }

                    cntr += 2;
                    double * tmp = stag(positions, s.size());
                    ret[(2*p*length) + (2*i)] = tmp[0];
                    ret[(2*p*length) + ((2*i)+1)] = tmp[1];
                    delete[] tmp;
                }
            }

            return ret;
        }

        int lenOut() {
            return 2*length*swarmSize;
        }
};