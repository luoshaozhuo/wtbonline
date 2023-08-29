FROM python:3.10.11
WORKDIR /app

COPY . .

RUN tar -zxvf TDengine-client-2.2.2.10-Linux-x64.tar.gz \
    && cd TDengine-client-2.2.2.10 \
    && ./install_client.sh \
    && cd .. \
    && mkdir /usr/share/fonts/chinese \
    && cp ./font/* /usr/share/fonts/chinese \
    && apt install -y pkg-config \
    && apt install -y libcairo2-dev \
    && apt install -y python3-dev \
    && apt install -y build-essential \
    && mkfontscale \
    && mkfontdir \
    && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD ["gunicorn", "run:server", "-c", "./gunicorn.conf.py"]
