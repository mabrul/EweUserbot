#==============×==============#
#      Created by: Alfa-Ex
#=========× AyiinXd ×=========#
# Izzy Ganteng

FROM ayiinxd/ayiin:xd

RUN git clone -b Ewe-Userbot https://github.com/mabrul/Ewe-Userbot /home/eweuserbot/ \
    && chmod 777 /home/eweuserbot\
    && mkdir /home/eweuserbot/bin/

#COPY ./sample.env ./.env* /home/eweuserbot/

WORKDIR /home/eweuserbot/

RUN pip install -r requirements.txt

CMD ["bash","start"]
