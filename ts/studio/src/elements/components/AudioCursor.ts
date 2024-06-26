import { AudioClock } from "./AudioClock";

export interface ICursorTimeline {
  domElement: HTMLElement;
  timeline: HTMLElement;
  cursor: AudioCursor;
  audioClock: AudioClock;
  beatWidth: number;
}

export class AudioCursor {
  readonly domElement: HTMLDivElement;

  constructor(readonly timeline: ICursorTimeline) {
    this.domElement = document.createElement("div");
    this.domElement.classList.add("audio-cursor");

    const clock = timeline.audioClock;

    clock.on("update", () => {
      this.update();
    });

    clock.on("start", () => {
      this.domElement.style.transform = "translateX(0)";
      this.domElement.style.display = "block";
      this.domElement.parentElement?.appendChild(this.domElement);
    });

    clock.on("stop", () => {
      this.domElement.style.display = "none";
    });
  }

  update() {
    this.domElement.style.transform = `translateX(${
      this.timeline.audioClock.currentBeat * this.timeline.beatWidth
    }px)`;
  }

  hide() {
    this.domElement.style.display = "none";
  }
}
