Please download ATSAS  deb package from their website.
	ATSAS-2.8.4-1_amd64.deb
Move this file to where the Dockerfile is and in that folder run:
	docker build -t idpfun .
Then you can run the docker container with all requirements with:
	docker run -it --rm -v ~/path/to/PED/:/home/PED/ -v ~/Projects/Chemes/IDPfun/PED-DB3/:/home/PED-DB3/ --volume="$HOME/.Xauthority:/root/.Xauthority:rw" --env="DISPLAY" --net=host  ubuntu:idpfun /bin/bash
This links the PED folder with sample data to a directory inside the docker's filesystem.