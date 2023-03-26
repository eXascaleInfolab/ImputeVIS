# options
#########################
# lengths <- seq.int(from = {start}, to = {end}, by = {tick});
#
# global_path <- "error/";
#
# output_mse <- paste(global_path, "mse/MSE_", sep="");
# output_rmse <- paste(global_path, "rmse/RMSE_", sep="");
# output_mae <- paste(global_path, "mae/MAE_", sep="");
# output_cor <- paste(global_path, "correlation.dat", sep="");
# input_missingmat <- paste("recovery/values/recovered_matrices/recoveredMat", sep="");
#
# list_algos <- c({allAlgos});

#########################

# algos_str = paste(list_algos, collapse="\t");
#
# TITLEBAR=paste("=====================================================",
# 	paste(" #  \t||  ref\t\t", algos_str, sep=""),
# 	"=====================================================\n", sep="\n");

# SEPARATE="=====================================================\n";

# msqe <- function() {
# 	dftest <- read.table(paste(input_missingmat, lengths[1], ".txt", sep=""), header=FALSE);
#
# 	for(i in 2:length(dftest)) {
# 		fileName = paste(output_mse, list_algos[i-1], ".dat", sep="");
# 		write(paste("#", list_algos[i-1]), fileName); #rewrite
# 	}
#
# 	for(len in lengths) {
# 		df <- read.table(paste(input_missingmat, len, ".txt", sep=""), header=FALSE);
# 		dfmx <- as.matrix(df);
# 		ref = dfmx[,1];
#
# 		for(i in 2:length(df)) {
# 			fileName = paste(output_mse, list_algos[i-1], ".dat", sep="");
# 			comp <- dfmx[,i];
# 			comp <- comp - ref;
# 			msqe_val <- mean(comp^2);
# 			#if (msqe_val > 1E10) { msqe_val = 30.0; }
# 			#else if (msqe_val > 25.0) { msqe_val = 25.0; }
# 			lin <- paste(len, " ", msqe_val, sep="");
# 			write(lin, fileName, append=TRUE);
# 		}
# 	}
# }

### Mutual Information
# Load infotheo package
library(infotheo)

# Define the time-series matrix and imputed time-series matrix
# Fake data to be replaced:
time_series_matrix <- matrix(runif(50), nrow = 10, ncol = 10)
imputed_matrix <- matrix(runif(50), nrow = 10, ncol = 10)

# Discretize continuous data
discretized_time_series <- discretize(time_series_matrix, nbins = 10)
discretized_imputed <- discretize(imputed_matrix, nbins = 10)

# Calculate mutual information for each pair of corresponding columns
mutual_info <- sapply(1:ncol(time_series_matrix), function(i) {
  mutinformation(discretized_time_series[, i], discretized_imputed[, i])
})

# For debug purposes Print mutual information values for each column
print(mutual_info)
