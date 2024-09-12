import os
import tempfile
import wave
import pyaudio
import keyboard
import pyautogui
import pyperclip
from groq import Groq

key="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"
client = Groq(api_key="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")

def grabar_audio(frecuencia_muestreo=16000, canales=1, fragmento=1024):
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=canales,
        rate=frecuencia_muestreo,
        input=True,
        frames_per_buffer=fragmento
    )
    print('Presiona y manten presionado el boton INSERT para comenzar a grabar...')
    frames = []
    keyboard.wait('insert')
    print('Grabando audio. Suelta el boton INSERT para detener la grabacion')
    while keyboard.is_pressed('insert'):
        data = stream.read(fragmento)
        frames.append(data)
    print('Grabacion finalizada')
    stream.stop_stream()
    stream.close()
    p.terminate()
    return frames, frecuencia_muestreo

def guardar_audio(frames, frecuencia_muestreo):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_temp:
        wf = wave.open(audio_temp.name, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
        wf.setframerate(frecuencia_muestreo)
        wf.close()
        return audio_temp.name
    
def transmitir_audio(ruta_archivo_audio):
    try:
        with open(ruta_archivo_audio, 'rb') as archivo:
            transcripcion = client.audio.transcriptions.create(
                file = (os.path.basename(ruta_archivo_audio), archivo.read()),
                model = "wispher-large-v3",
                prompt = """El audio es de una persona que está trabajando""",
                response_format = "text",
                language = "es"
            )
        return transcripcion
    except Exception as e:
        print(e)
        return None

def copiar_transcripcion_al_portapapeles(texto):
    pyperclip.copy(texto)
    pyautogui.hotkey('ctrl', 'v')

   
def main():
    while True:
        frames, frecuencia_muestreo = grabar_audio()
        archivo_audio_temp = guardar_audio(frames, frecuencia_muestreo)
        print ("Transcribiendo...")
        transcripcion = transmitir_audio(archivo_audio_temp)
        if transcripcion:
            print ("Transcripción:")
            print ("copiando la transcripcion al cortapapeles...")
            copiar_transcripcion_al_portapapeles(transcripcion)
            print ("Transcripción copiada al portapapeles y pegada en la aplicación")
        else:
            print ("No se pudo transmitir el audio, intentelo de nuevo")
        os.unlink(archivo_audio_temp)
        print ("Listo para la proxima transcripción. Presiona INSERTAR para comenzar")

if __name__ == "__main__":
    main()