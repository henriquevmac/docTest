import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { MarkdownModule } from 'ngx-markdown';

const API_URL = 'https://doc-test-api-301874410303.europe-west1.run.app/run';
// const API_URL = 'http://localhost:8000/run';
const MODEL_NAME = 'doc-test-model'

type ChatMessage = {
  role: 'user' | 'model';
  text: string;
}

type MessagePart = {
  text: string;
}

type ApiMessage = {
  parts: MessagePart[];
  role: "user" | "model"
}

type ApiRequestBody = {
  appName: typeof MODEL_NAME;
  userId: string;
  sessionId: string;
  newMessage: ApiMessage;
  streaming: boolean;
}

type ApiResponse = {
  actions: Object;
  author: string;
  content: ApiMessage
  finish_reason: string;
  id: string;
  invocationId: string;
  timestamp: number;
  usageMetadata: Object;
}

@Component({
  selector: 'app-chat',
  imports: [CommonModule, FormsModule, MarkdownModule],
  templateUrl: './chat.html',
  styleUrl: './chat.css'
})
export class Chat {
  messages = signal<ChatMessage[]>([]);
  loading = signal(false);
  draft = '';

  constructor(private http: HttpClient) {}

  send() {
    const text = this.draft.trim();
    if (!text || this.loading()) return;

    // Append user message
    this.messages.update(arr => [...arr, { role: 'user', text }]);
    this.draft = '';
    this.loading.set(true);

    var requestBody: ApiRequestBody = {
      appName: MODEL_NAME,
      userId: "0",
      sessionId: "0",
      newMessage: {
        parts: [{ text: text }],
        role: "user"
      },
      streaming: false
    }

    // POST to Python API (adjust URL and payload to match backend)
    this.http.post<ApiResponse[]>(API_URL, requestBody)
      .subscribe({
      next: (res) => {
        var messages = '';
        for (var obj of res) {
          for (var part of obj.content.parts) {
            if (part.text) {
              var newMessages = part.text.concat(messages, '\n');
              messages = newMessages;
            }
          }
        }
        this.messages.update(arr => [...arr, { role: 'model', text: messages }]);
        this.loading.set(false);
      },
      error: (err) => {
        this.messages.update(arr => [...arr, { role: 'model', text: 'Error contacting server.' }]);
        this.loading.set(false);
        console.error(err);
      }
    });
  }
}
