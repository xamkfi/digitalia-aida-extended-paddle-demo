FROM python:3.9
WORKDIR /app/paddleOCR
ENV PYTHONBUFFERED=0
RUN pip install paddlepaddle==2.5.2
RUN pip install "paddleocr>=2.0.1" 
RUN pip install gradio
RUN pip install PyMuPDF
RUN pip install python-magic
RUN pip install numpy
RUn pip install pillow
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
COPY . .
CMD ["python", "extendedPaddleOCR.py"]
EXPOSE 8087