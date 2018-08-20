FROM debian:latest
RUN apt-get update && apt-get install bash-completion python3 python3-pip python-dev r-base gawk git subversion curl
RUN mkdir -p /home/software/ && \
	cd /home/software/ && \
	git clone https://github.com/rlabduke/MolProbity.git --branch molprobity_4.4 --single-branch --depth 1  && \
	cd MolProbity && \
	./configure.sh