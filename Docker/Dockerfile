FROM debian:latest
RUN apt-get -y update && \
	apt-get -y install apt-utils && \
	apt-get -y install \
		bash-completion \
		python3 \
		python3-pip \
		python-dev \
		r-base \
		gawk git \
		subversion \
		curl \
		libcairo2-dev \
		libxt-dev

RUN R -e "install.packages(c('data.table', 'Cairo'), repos = 'https://cran.stat.unipd.it/')"

RUN pip3 install pandas biopython

RUN mkdir -p /home/software/atsas \
	cd /home/software/ && \
	git clone https://github.com/rlabduke/MolProbity.git --branch molprobity_4.4 --single-branch --depth 1  && \
	cd MolProbity && \
	./configure.sh

COPY ./ATSAS-2.8.4-1_amd64.deb /home/software/atsas/
RUN dpkg -i /home/software/atsas/ATSAS-2.8.4-1_amd64.deb && apt-get install -f