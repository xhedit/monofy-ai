import EventObject from "../../../../elements/src/EventObject";
import { getAudioContext } from "../../../../elements/src/managers/AudioManager";

/**
 * Represents an audio clock that provides functionality for controlling audio playback and scheduling events.
 */
export class AudioClock extends EventObject<
  "start" | "stop" | "pause" | "update"
> {
  domElement: HTMLDivElement;
  bpmInput: HTMLInputElement;
  playPauseButton: HTMLButtonElement;
  stopButton: HTMLButtonElement;
  currentTimeDisplay: HTMLSpanElement;
  private _bpm: number = 100;
  private _scheduledEvents: {
    source: AudioBufferSourceNode;
    time: number;
    callback: () => void;
  }[] = [];
  private _startTime: number | null = null;

  get startTime(): number | null {
    return this._startTime;
  }

  get currentBeat(): number {
    const elapsedTime =
      this._startTime !== null
        ? getAudioContext().currentTime - this._startTime
        : 0;
    return elapsedTime * (this._bpm / 60);
  }

  get isPlaying(): boolean {
    return this._startTime != null && this._startTime >= 0;
  }

  get bpm(): number {
    return this._bpm;
  }

  constructor() {
    super();

    this.domElement = document.createElement("div");
    this.domElement.classList.add("audio-clock");

    this.playPauseButton = document.createElement("button");
    this.playPauseButton.classList.add("audio-clock-play-pause");
    this.playPauseButton.textContent = "Play";

    this.playPauseButton.addEventListener("click", () => {
      if (this.isPlaying) {
        this.stop();
      } else {
        getAudioContext();
        this.playPause();
      }
    });
    this.domElement.appendChild(this.playPauseButton);
    this.stopButton = document.createElement("button");
    this.stopButton.classList.add("audio-clock-stop");
    this.stopButton.textContent = "Stop";

    this.stopButton.addEventListener("click", () => {
      this.stop();
    });
    this.domElement.appendChild(this.stopButton);

    this.bpmInput = document.createElement("input");
    this.bpmInput.classList.add("audio-clock-bpm");
    this.bpmInput.type = "number";
    this.bpmInput.value = "120";

    this.bpmInput.addEventListener("input", () => {
      this._bpm = parseFloat(this.bpmInput.value);
    });
    this.domElement.appendChild(this.bpmInput);

    this.currentTimeDisplay = document.createElement("span");
    this.currentTimeDisplay.classList.add("audio-clock-time");
    this.currentTimeDisplay.textContent = "01:1";

    this.domElement.appendChild(this.currentTimeDisplay);
  }

  start(): void {
    this._startTime = getAudioContext().currentTime;
    console.log("Started at", this._startTime);
    requestAnimationFrame(this._render.bind(this));
    this.emit("start");
  }

  private _render(): void {
    this._update(this.currentBeat);
    this.emit("update");
    if (this.isPlaying) requestAnimationFrame(this._render.bind(this));
  }

  stop(): void {
    this.emit("stop");
    this._startTime = null;

    for (const { source } of this._scheduledEvents) {
      source.stop();
      source.disconnect();
    }
    this._scheduledEvents = [];

    this._update(this.currentBeat);
    this.playPauseButton.textContent = "Play";
  }

  restart() {
    if (this.isPlaying) {
      this._startTime = getAudioContext().currentTime;
    }
  }

  playPause(): void {
    if (this.isPlaying) {
      this.stop(); // TODO: This should be a pause
    } else {
      const audioContext = getAudioContext();

      const buffer = audioContext.createBuffer(1, 1, audioContext.sampleRate);
      const source = audioContext.createBufferSource();
      source.buffer = buffer;
      source.connect(audioContext.destination);
      source.start();

      this.start();
    }
    this.playPauseButton.textContent = this.isPlaying ? "Pause" : "Play";
  }

  private _update(beat: number): void {
    const bars = Math.floor(beat / 4) + 1;
    const beats = Math.floor(beat % 4) + 1;
    const timeString = `${bars
      .toString()
      .padStart(2, "0")}:${beats.toString()}`;
    this.currentTimeDisplay.textContent = timeString;
  }

  /**
   * Schedules UI event to occur at a specific time during audio playback. This should not be used for scheduling audio events.
   */
  scheduleEventAtTime(callback: () => void, time: number): void {
    const audioContext = getAudioContext();
    const emptyBuffer = audioContext.createBuffer(
      1,
      1,
      audioContext.sampleRate
    );
    const source = audioContext.createBufferSource();
    source.buffer = emptyBuffer;
    source.connect(audioContext.destination);
    source.onended = () => callback();
    source.start(time);
    this._scheduledEvents.push({ source, time, callback });
  }

  /**
   * Schedules UI event to occur at a specific time during audio playback. This should not be used for scheduling audio events.
   */
  scheduleEventAtBeat(callback: () => void, beat: number): void {
    const time = this._startTime! + (beat / this._bpm) * 60;
    this.scheduleEventAtTime(callback, time);
  }
}
