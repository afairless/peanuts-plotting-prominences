
library(ggplot2)
library(zoo)

all <- read.csv('proportions_with_chars_by_comic_1_overall.csv', header=T)

#sum(is.na(all))
#col_na_sums <- sapply(all, function(nas) sum(length(which(is.na(nas)))))

all[is.na(all)] <- 0
all$school[is.infinite(all$school)] <- 0

# re-arrange columns so that most-used characters appear first
col_sums <- data.frame(colSums(all[ , 2:dim(all)[2]]))
col_order <- order(col_sums[ , 1], decreasing=T)
col_order <- append(c(1), col_order + 1)
all_ordered <- all[ , col_order]   

# create data frame with only the most-used characters
drop_col_names <- c('snoopy', 'peppermint', 'school', 'world.famous', 
                   'flying.ace', 'literary.ace', 'beaglescout', 'santa', 'joe')
top_characters <- all_ordered[ , !(names(all_ordered) %in% drop_col_names)]
last_col_index <- which(colnames(top_characters) == 'franklin')  # Franklin is least-used character to be included
top_characters <- top_characters[ , 1:last_col_index]
colnames(top_characters)[3] <- 'snoopy'

# specify years with which to label x-axis and get their indices
get_year_start_idx <- function(year, dates) {
     year_start_idx <- which(substr(dates, 1, 4) == as.character(year))[1]
     return(year_start_idx)
}
year_labels = seq(from=1955, to=1995, by=5)
year_start_idx <- sapply(year_labels, get_year_start_idx, top_characters$filename)


# cases = dim(top_characters)[1]
# cbs = data.frame(cbind(1:cases, top_characters[1:cases, 2:3], top_characters$peppermint.patty))
# colnames(cbs) <- c('index', 'cb', 'snoopy', 'pep')
# k = 300
# ggplot(cbs, aes(index, cb)) +
#      geom_line(aes(y=rollmean(cbs$cb, k=k, fill=NA)), col=2) +
#      geom_line(aes(y=rollmean(cbs$snoopy, k=k, fill=NA)), col=4) +
#      geom_line(aes(y=rollmean(cbs$pep, k=k, fill=NA)), col=3) 


capitalize <- function(a_string) {
     # capitalize each word in a string where words are separated by a period '.'
     a_string <- gsub('\\.', ' ', a_string)
     separator = ' '
     sub_str <- strsplit(a_string, separator)[[1]]
     capitalized <-paste(toupper(substring(sub_str, 1, 1)), substring(sub_str, 2),
                         sep='', collapse='.')
     return(capitalized)
}


library(reshape2)
characters_only <- top_characters[ , 2:dim(top_characters)[2]]
colnames(characters_only) <- sapply(colnames(characters_only), capitalize)


# calculate rolling average

# # roll_mean <- sapply(characters_only, rollmean, 500, NA)     # static rolling window
# # dynamic rolling window for moving/rolling averages
# windows <- c(rep(100, 200), rep(300, 600), rep(600, 1200), rep(1200, 13931),
#              rep(600, 1200), rep(300, 600), rep(100, 200))
# roll_mean <- rollapply(characters_only, width=windows, mean, by.column=T, fill=NA)
# roll_mean <- data.frame(cbind(1:dim(characters_only)[1], roll_mean))
# colnames(roll_mean)[1] <- 'index'
# 
# # applying rolling average leaves how many initial values blank, i.e., 'NA'?
# # the NAs won't be plotted, so offset is used to adjust x-axis labels
# offset <- which(!is.na(roll_mean[ , 2]))[1] - 1

dynamic_margin <- function(a_vector, window_size, margin_size) {
     rolling_margin <- rep(NA, length(margin_size))
     window_mid <- round(window_size / 2)
     transition_step <- margin_size / window_mid
     for (i in 1:margin_size) {
          start_idx_diff <- trunc(i / transition_step)
          window_start <- i - start_idx_diff
          window_end <- window_start + window_size - 1
          rolling_margin[i] <- mean(a_vector[window_start:window_end])
          # print(c(i, start_idx_diff, window_start, window_start + start_idx_diff, window_end, rolling_margin[i]))
     }
     return(rolling_margin)
}


dynamic_rolling_average <- function(a_vector, window_size, margin_size) {
     # Problem:  Calculating rolling averages across a series of data points
     #    requires trimming the data points at the end so that they are not used
     #    in the calculations
     # Rolling averages are calculated across a moving window of consecutive
     #    data points.  The position of the data point of interest is always in
     #    the middle of the window.
     # Solution:  When the data point of interest is at the start/end/edge of
     #    the data series, allow it to be at the edge of the window.  As the
     #    calculation of the average rolls/advances through the data series,
     #    gradually move the data point's position from the edge to the middle
     #    of the window.
     # 
     # 'a_vector' - a vector containing a numeric data series
     # 'window_size' - the number of data points across which to calculate the
     #    rolling average
     # 'margin_size' - the size of the each margin at either end of the data
     #    series; at the exterior end of the margin, the data point of interest
     #    is at the edge of the window; at the interior end of the margin, the
     #    data point of interest is at the middle of the margin
     # 
     # To clarify and summarize:
     # Thus, a data series is divided into three parts:  a margin, the middle,
     #    and the other margin.  In the middle of the data series, the rolling
     #    average is calculated as it usually is with the data point of interest
     #    in the middle of the window.  In the margins, as one moves from an
     #    edge of the data series towards its middle, the data point of interest
     #    gradually shifts from the edge of the window towards the middle of
     #    the window so that it reaches the middle of the window by the time it
     #    reaches the interior edge of the margin.
     mean_vector <- rep(NA, length(a_vector))
     mean_vector[1:margin_size] <- dynamic_margin(a_vector, window_size, margin_size)
     end <- length(mean_vector)
     end_margin <- length(mean_vector) - margin_size
     reversed_vector <- rev(a_vector)
     mean_vector[end:(end_margin+1)] <- dynamic_margin(reversed_vector,
                                                       window_size, margin_size)
     for (i in (margin_size+1):end_margin) {
          window_half <- round(window_size / 2)
          window_start <- i - window_half
          window_end <- window_start + window_size - 1
          mean_vector[i] <- mean(a_vector[window_start:window_end])
     }
     return(mean_vector)
}


window_size <- 1095
margin_size <- window_size * 3
roll_mean <- sapply(characters_only, dynamic_rolling_average, window_size, margin_size)
roll_mean <- data.frame(cbind(1:dim(characters_only)[1], roll_mean))
colnames(roll_mean)[1] <- 'index'

# reshape data frame so that ggplot2 will plot multiple series
melt_roll_mean <- melt(roll_mean, id=colnames(roll_mean)[1])

# colors custom-chosen for each character, mostly based on clothing
# e.g., Charlie Brown's yellow shirt or Lucy's dark blue dress
char_colors = c('yellow', 'white', 'blue', 'red', 'green', 'lightskyblue',
                'orange', 'yellow', 'purple', 'orange', 'purple', 'red',
                'white', 'palegreen3', 'brown', 'orangered', 'brown')
colors_rgb <- t(sapply(char_colors, FUN=col2rgb))
colnames(colors_rgb) <- c('red', 'green', 'blue')
write.csv(colors_rgb, 'character_colors.csv', row.names=T)

bkgd='gray20'
ggplot(melt_roll_mean, aes(x=index, y=value, color=variable, group=variable)) +
     geom_line() +
     scale_color_manual(values=char_colors) +
     theme(panel.background=element_rect(fill=bkgd)) +
     theme(legend.key=element_rect(fill=bkgd)) +
     theme(panel.grid.major=element_line(color='gray27')) +
     theme(panel.grid.minor=element_blank()) +
     labs(title='Prominence of Characters in the Peanuts Comic Strip') +
     theme(plot.title=element_text(hjust=0.5)) +
     xlab('Comic strip dates') +
     ylab('Proportion of comic strip panels in which character appears or is mentioned') +
     theme(legend.title=element_blank()) +
     scale_x_continuous(breaks=year_start_idx - offset, labels=year_labels)

ggsave('proportions_with_chars_by_comic_1_overall.png', width=11.5, height=7)

