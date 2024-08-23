#!/usr/bin/env python
# coding: utf-8

# In[1]:


#from PIL import Image
from paddleocr import PaddleOCR
import magic
import numpy as np
#from tqdm import tqdm
import gradio as gr
import os
import PIL
from PIL import Image



model_path = './models'

ocr = PaddleOCR(lang='latin', det=True, use_angle_cls=True, rec_model_dir=model_path, show_log=False,)

def tifftopng(tiffPath, jpgPath):
    # Open the tiff image
    tiff_image = Image.open(tiffPath)

    # Save as PNG
    tiff_image.save(jpgPath)
    return jpgPath

def primaryHandler(upFile): #/tmp/gradio/a2270f1e67eb1b9ceb884cde01ceb85f046f23d9/F1_0058.tif    
    upFileName = os.path.split(upFile)[1]    
    mime = checkForImage((upFile))
    print (mime)
    mimetype, detail = mime.split('/')
    if mimetype=="image":
        #if tiff, convert to png before processing
        if detail=="tiff":
            pngFile = "{}.jpg".format(upFile)
            upFile = tifftopng(upFile, pngFile)
            print("File after conversion: {}".format(upFile))
        
        outputimage = PIL.Image.open(upFile)
        #If image try to ocr
        res = ocr.ocr(upFile, cls=True)        
        print("Image {} opened".format(upFile))
        draw = PIL.ImageDraw.Draw(outputimage)
        rettext = ""
        #print("Full response : {}".format(res))
        plaintextResponse = ""
        totalAccuracy = []
        try:
            for i in res[0]:
                #print(i)
                text = i[1][0]
                box = np.array(i[0]).astype(np.int32)
                #box = i[0]                
                acc = float(i[1][1])
                #print(box)
                xmin = min(box[:, 0])
                ymin = min(box[:, 1])
                xmax = max(box[:, 0])
                ymax = max(box[:, 1])
                #print(acc)
                if acc > 0.95:
                    draw.rectangle((xmin, ymin, xmax, ymax), outline="green", width=3)
                elif 0.85 < acc <=0.95:
                    draw.rectangle((xmin, ymin, xmax, ymax), outline="yellow", width=3)
                elif 0.75 < acc <=0.85:
                    draw.rectangle((xmin, ymin, xmax, ymax), outline="orange", width=3)
                else:
                    draw.rectangle((xmin, ymin, xmax, ymax), outline="red", width=3)
                #draw.text((xmin, ymin), f"{i}", fill="black")                
                rettext += "{}-{}%\n".format(text, acc)
                plaintextResponse+="{}\n".format(text)
                totalAccuracy.append(acc)
        except Exception:
            rettext+="Ei tunnistettua tekstiä kuvassa"
            gr.Info("Ei tunnistettua tekstiä kuvassa")
            #raise gr.Error("No identifed text in picture")
            
    else:
        gr.Info("Väärä mime tyyppi, {}".format(mime))
        rettext = "OCR luku on vain kuville, ei {} tyyppisille tiedostoille!".format(mime)
    #print("avg count")
    avg = round(sum(totalAccuracy)/len(totalAccuracy)*100 ,2)
    textfile = upFileName+".txt"
    with open(textfile, 'w') as f:
        f.write(plaintextResponse)
            
    print(rettext)
    return plaintextResponse, avg, textfile, outputimage


def checkForImage(upFile):
    mime = magic.Magic(mime=True)
    return mime.from_file(upFile)    
        
        
if __name__ == '__main__':    
    print(gr.__version__)
    snkey = "./snakeoil/snakeoil.key"
    sncert="./snakeoil/snakeoil.crt"
    """
    webui = gr.Interface(
        fn=primaryHandler,
        title="AIDA Paddle OCR Demo",
        description="Tämä demo käyttää AIDA -projektin jatko-opettamaa PaddleOCR moottoria",
        #inputs=gr.Image(),
        inputs=gr.File(label="Uppaa tähän kuvatiedosto"),
        outputs=[gr.Textbox(label="OCR tulokset")]
        )
        """
    

    with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue", secondary_hue="stone")) as webui:      
        gr.Markdown("# AIDA projektin Paddle OCR demo - piirtää myös boxit")
        gr.Markdown("Käyttää AIDA projektissa jatko-opetettua PaddleOCR moottoria")
        gr.Markdown("Huom! Voit ladata vain yhden tiedoston kerrallaan ja tiedoston tulee olla yleinen kuvaformaatti")
        gr.Markdown("# Käsittely")
        with gr.Row():
            inputdata = gr.File(label="Uppaa tähän kuva")
        btn = gr.Button("OCR-lue")
        gr.Markdown("# Tulokset")
        with gr.Row():
            textoutputdata = gr.TextArea(label="OCR tulokset")   
            with gr.Column():
                accuracyOutput = gr.Text(label="Tarkkuus")
                fileDownload = gr.File(label="Lataa tekstinä")
        gr.Markdown("Huom! Tarkkuus perustuu ainoastaan PaddleOCR:n omaan rivikohtaiseen arvioon tunnistuksen tarkkuudesta.")
        gr.Markdown("Kuvassa punainen < 75%, oranssi 75-85%, keltainen 85-95% ja  vihreä yli 95%")
        annotated = gr.Image(label="Laatikoitu kuva")
                
        
        btn.click(fn=primaryHandler, inputs=inputdata, outputs=[textoutputdata, accuracyOutput, fileDownload, annotated])
        
    #webui.launch(server_name="0.0.0.0", server_port=8087 )
    webui.launch(server_name="0.0.0.0", server_port=8087, root_path="/AIDA/extended-paddle-demo", ssl_keyfile=snkey, ssl_certfile=sncert, ssl_verify=False)
    #demo.launch(server_name="0.0.0.0", server_port=8081, root_path="/ai-demo", ssl_keyfile="./snakeoil/snakeoil.key", ssl_certfile="./snakeoil/snakeoil.crt", ssl_verify=False)
    

