FROM nginx:1.15.2

USER root
RUN rm /etc/localtime && ln -s /usr/share/zoneinfo/Europe/Zurich /etc/localtime
RUN echo "Europe/Zurich" > /etc/timezone

RUN apt update && apt install -y locales && rm -rf /var/lib/apt/lists/*
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/fr_CH.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
ENV LANG fr_CH.UTF-8  
	

## Remove default Nginx website
RUN rm -rf /usr/share/nginx/html/*


COPY webapp.conf /etc/nginx/conf.d/webapp.conf

COPY  ./dist/front /usr/share/nginx/html/

RUN chmod 777 -R /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]
