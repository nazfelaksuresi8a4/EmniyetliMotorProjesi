int accelometer = A0;
int buzzer = 2;
int relay = 5;

int state = 0;

int activated_led = 8;
int deactivated_led = 9;

void call_buzzer(String x){
  if (x == "call_low"){
    tone(buzzer,440);
    delay(500);
    noTone(buzzer);
  }
  else if (x == "call_high"){
    tone(buzzer,880);
    delay(500);
    noTone(buzzer);

  }
}

void call_led(String x){
  if (x == "activated"){
    digitalWrite(activated_led,HIGH);
    digitalWrite(deactivated_led,LOW);
  }
  else if (x == "deactivated"){
    digitalWrite(activated_led,LOW);
    digitalWrite(deactivated_led,HIGH);
  }
}

void setup(){
  Serial.begin(9600);

  pinMode(buzzer,OUTPUT);
  pinMode(relay,OUTPUT);

  pinMode(activated_led,OUTPUT);
  pinMode(deactivated_led,OUTPUT);

  digitalWrite(relay,HIGH);

}

void loop(){
  char decision = Serial.read();
  if (Serial.available() > 0){

    if (state != 1 && decision == '1'){
      digitalWrite(relay,LOW);
      call_buzzer("call_high");
      call_led("activated");
      state = 1;
    }
    else if (state != 0 && decision == '0'){
      digitalWrite(relay,HIGH);
      call_buzzer("call_low");
      call_led("deactivated");
      state = 0;
    }
  }
  int accelometer_value = analogRead(accelometer);
  Serial.println(accelometer_value);
}
