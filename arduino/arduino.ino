#include <SD.h>
#include <SPI.h>
#include <TMRpcm.h>
File myFile;

#define SD_ChipSelectPin 10  //using digital pin 4 on arduino nano 328, can use other pins

TMRpcm audio1;// create an object for use in this sketch 
TMRpcm audio2;
TMRpcm audio3;
TMRpcm audio4;
int buttonState1 = 0;
int buttonState2 = 0;
int buttonState3=0;
char c, d, e, f;
void setup() {

Serial.begin(115200);

  if (!SD.begin(SD_ChipSelectPin))
  {
    Serial.println("SD Fail");
    return;
  }
  else {
    Serial.println("SD OK");
  }
  // The audio library needs to know which CS pin to use for recording
audio1.CSPin = SD_ChipSelectPin;
//audio2.CSPin = SD_ChipSelectPin;
//audio3.CSPin = SD_ChipSelectPin;
//audio4.CSPin = SD_ChipSelectPin;
pinMode(2, INPUT);
pinMode(3, INPUT);
pinMode(4,INPUT);

}


void loop() {

buttonState1 = digitalRead(2);
buttonState2 = digitalRead(3);
buttonState3=digitalRead(4);

  if (buttonState1 == HIGH) 
  { // 若按键1被按下
    delay(200);//等待跳过按键抖动的不稳定过程
    if (buttonState1 == HIGH)
    {
      c = 'r';// 开始录音
    }
  }

  //***************************************
  if (buttonState2 == HIGH) {//按键2
    delay(500);//等待跳过按键抖动的不稳定过程
    if (buttonState2 == HIGH)
    {
      c = 'S';
    }

  }

  //***********************************
   if (buttonState3 == HIGH){
    {
      c = 't';
    }
   }
   //****************************
switch (c) {
    case 'r':
    audio1.startRecording("test1.wav", 20000, A0);  Serial.println("1start");
    delay(5000);
     audio1.stopRecording("test1.wav"); Serial.println("1stop");break;
    //audio2.startRecording("test2.wav", 8000, A1);  Serial.println("2start");
    //audio3.startRecording("test3.wav", 8000, A2);  Serial.println("3start");
    //audio4.startRecording("test4.wav", 8000, A3);  Serial.println("4start"); break;
    //case 'R': audio.startRecording("test.wav",16000,A0,1); break;  //Record, but with passthrough to speaker.
    //case 't': audio.startRecording("test.wav",16000,A0,2); break;  //Do not record. Output direct to speaker
    //Note: If samples are dropped before writing, it
    //      will not be heard in passthrough mode
    //case 's': audio.stopRecording("test.wav"); break;              //Stop recording
    //case 'p': audio.play("test.wav"); break;                       //Play the recording 
    //case '=': audio.volume(1); break;                              //Increase volume by 1. Does not affect recording
    //case '-': audio.volume(0); break;                              //Decrease volume by 1. Does not affect recording
  case 'S':
    //audio1.stopRecording("test1.wav"); Serial.println("1stop");
    myFile = SD.open("TEST1.WAV");
  if (myFile) {
    //Serial.println("TEST1.WAV:");
    while (myFile.available()) {
            Serial.write(myFile.read());
    }
    myFile.close();
  } else {
    Serial.println("error opening TEST1.WAV");
  };
  ;break;
    //audio2.stopRecording("tes2t.wav");;Serial.println("2stop");
    //audio3.stopRecording("test3.wav"); Serial.println("3stop");
    //audio4.stopRecording("test4.wav"); Serial.println("4stop"); break;//Stop all playback
    case't': myFile = SD.open("TEST1.txt");
  if (myFile) {
    //Serial.println("TEST1.txt:");
    while (myFile.available()) {
            Serial.write(myFile.read());
    }
    myFile.close();
  } else {
    Serial.println("error opening TEST1.txt");
  };
  //Serial.println("upload");break;
    //这里放上传

  };

  c = 'l';

  delay(500);
}
