import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class VoiceRecorderService {
  readonly isRecording = signal(false);
  readonly transcript = signal('');
  readonly error = signal<string | null>(null);

  private mediaRecorder: MediaRecorder | null = null;
  private chunks: Blob[] = [];
  private recognition: any = null;
  private finalTranscript = '';

  startRecording(): Promise<void> {
    this.error.set(null);
    this.transcript.set('');
    this.finalTranscript = '';

    // Try Web Speech API first
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      return this.startSpeechRecognition(SpeechRecognition);
    }

    // Fallback to MediaRecorder
    return this.startMediaRecorder();
  }

  stopRecording(): Blob | null {
    this.isRecording.set(false);

    if (this.recognition) {
      this.recognition.stop();
      this.recognition = null;
      return null; // Speech API handles transcript directly
    }

    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop();
      const blob = new Blob(this.chunks, { type: 'audio/webm' });
      this.chunks = [];
      return blob;
    }

    return null;
  }

  private startSpeechRecognition(SpeechRecognition: any): Promise<void> {
    return new Promise((resolve, reject) => {
      this.recognition = new SpeechRecognition();
      this.recognition.lang = 'fr-FR';
      this.recognition.continuous = true;
      this.recognition.interimResults = true;

      this.recognition.onstart = () => {
        this.isRecording.set(true);
        resolve();
      };

      this.recognition.onresult = (event: any) => {
        let interim = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            this.finalTranscript += event.results[i][0].transcript + ' ';
          } else {
            interim += event.results[i][0].transcript;
          }
        }
        this.transcript.set(this.finalTranscript + interim);
      };

      this.recognition.onerror = (event: any) => {
        this.error.set(`Erreur reconnaissance vocale: ${event.error}`);
        this.isRecording.set(false);
        reject(event.error);
      };

      this.recognition.onend = () => {
        if (this.isRecording()) {
          // Auto-restart: Web Speech API sometimes stops after silence
          try {
            this.recognition.start();
          } catch {
            this.isRecording.set(false);
          }
        }
      };

      this.recognition.start();
    });
  }

  private async startMediaRecorder(): Promise<void> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(stream);
      this.chunks = [];

      this.mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) this.chunks.push(e.data);
      };

      this.mediaRecorder.start();
      this.isRecording.set(true);
    } catch (err) {
      this.error.set("Impossible d'acceder au microphone");
      throw err;
    }
  }
}
