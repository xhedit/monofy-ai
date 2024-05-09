import EventObject from "../../../../elements/src/EventObject";
import {
  DEFAULT_NOTE_HEIGHT,
  NOTE_NAMES,
} from "../../constants";
import { PatternTrack } from "./PatternTrack";
import { LyricEditorDialog } from "../audioDialogs";
import { IEventItem } from "../../schema";

function getNoteNameFromPitch(pitch: number): string {
  const note = NOTE_NAMES[pitch % NOTE_NAMES.length];
  return `${note}${Math.floor(pitch / NOTE_NAMES.length)}`;
}

const NOTE_HANDLE_WIDTH = 6;

export class GridItem {
  note: number;
  start: number;
  duration: number;
  velocity: number = 100;
  label: string | "" = "";
  domElement: HTMLDivElement;
  noteLabel: HTMLDivElement;
  lyricLabel: HTMLDivElement;
  audio: AudioBuffer | null = null;

  constructor(
    private readonly grid: Grid,
    item: IEventItem
  ) {
    this.note = item.note;
    this.start = item.start;
    this.duration = item.duration;
    this.domElement = document.createElement("div");
    this.domElement.classList.add("piano-roll-note");
    this.domElement.style.height = `${grid.noteHeight}px`;

    this.noteLabel = document.createElement("div");
    this.noteLabel.classList.add("piano-roll-note-label");
    this.noteLabel.textContent = getNoteNameFromPitch(this.note);
    this.domElement.appendChild(this.noteLabel);

    this.lyricLabel = document.createElement("div");
    this.lyricLabel.classList.add("piano-roll-note-lyric");
    this.domElement.appendChild(this.lyricLabel);

    if (item.label) this.lyricLabel.textContent = item.label;

    console.log("GridItem", this);

    grid.gridElement.appendChild(this.domElement);
  }
}

export class Grid extends EventObject<"update"> {
  readonly domElement: HTMLDivElement;
  readonly gridElement: HTMLDivElement;
  readonly previewCanvas: HTMLCanvasElement;
  readonly noteHeight = DEFAULT_NOTE_HEIGHT;
  readonly beatWidth = 100;
  readonly noteEditor: LyricEditorDialog;
  private _currentNote: GridItem | null = null;
  private _dragMode: string | null = null;
  private _quantize: number = 0.25;
  private _dragOffset: number = 0;
  private _track: PatternTrack | null = null;

  constructor() {
    super();

    this.domElement = document.createElement("div");
    this.domElement.classList.add("piano-roll-grid-container");

    this.gridElement = document.createElement("div");
    this.gridElement.classList.add("piano-roll-grid");

    this.previewCanvas = document.createElement("canvas");
    this.previewCanvas.style.imageRendering = "pixelated";

    const rowBackgroundCanvas = document.createElement("canvas");
    rowBackgroundCanvas.style.imageRendering = "pixelated";
    rowBackgroundCanvas.width = this.beatWidth * 4;
    rowBackgroundCanvas.height = this.noteHeight;
    console.log("debug", rowBackgroundCanvas.width, rowBackgroundCanvas.height);
    const ctx = rowBackgroundCanvas.getContext("2d");
    // disable anti-alias

    if (ctx) {
      ctx.strokeStyle = "#666";
      ctx.lineWidth = 0.5;
      for (let j = 1; j < 4; j++) {
        ctx.beginPath();
        ctx.moveTo(j * this.beatWidth, 0);
        ctx.lineTo(j * this.beatWidth, this.noteHeight);
        ctx.stroke();
      }
      ctx.lineWidth = 1;
      ctx.strokeStyle = "white";
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(0, this.noteHeight);
      ctx.stroke();
    }
    for (let i = 0; i < 88; i++) {
      const row = document.createElement("div");
      row.classList.add("piano-roll-grid-row");
      row.style.height = `${this.noteHeight}px`;
      this.gridElement.appendChild(row);
      const base64 = rowBackgroundCanvas.toDataURL();
      row.style.backgroundImage = `url(${base64})`;
      row.style.backgroundRepeat = "repeat";
    }
    this.domElement.appendChild(this.gridElement);

    this.noteEditor = new LyricEditorDialog((note) => {
      const input = this.noteEditor.domElement.querySelector(
        ".lyric-editor-text"
      ) as HTMLInputElement;
      note.label = input?.value || "";
    });

    document.body.appendChild(this.noteEditor.domElement);

    this.gridElement.addEventListener("pointerdown", (event) => {
      if (!this._track) throw new Error("No track");

      if (!this._track.events) throw new Error("No events");

      this._dragOffset = event.layerX;
      event.preventDefault();
      if (this.noteEditor.domElement.style.display === "block") {
        this.noteEditor.domElement.style.display = "none";
        return;
      }

      if (
        event.target instanceof HTMLDivElement &&
        event.target.classList.contains("piano-roll-note")
      ) {
        this.gridElement.classList.add("dragging");
        const note = this._track.events.find(
          (n) => n.domElement === event.target
        );

        if (event.ctrlKey || event.button === 1) {
          if (note)
            this.noteEditor.show(event.clientX + 20, event.clientY - 5, note);
          else this.noteEditor.domElement.style.display = "none";
        }

        if (note) {
          this._currentNote = note;

          if (event.button === 2) {
            this.remove(note);
            this._currentNote = null;
          } else {
            note.domElement.parentElement?.appendChild(note.domElement);
            if (this._dragOffset < NOTE_HANDLE_WIDTH) {
              this._dragMode = "start";
            } else if (
              note.domElement.offsetWidth - this._dragOffset <
              NOTE_HANDLE_WIDTH
            ) {
              this._dragMode = "end";
            } else {
              this._dragMode = "move";
            }
          }
        }
      } else if (event.button !== 0) return;
      else if (event.target === this.gridElement) {
        this.gridElement.classList.add("dragging");
        const pitch = 87 - Math.floor(event.layerY / this.noteHeight);

        let start = event.layerX / this.beatWidth;
        start = Math.round(start / this._quantize) * this._quantize;
        console.log("start", start, event.layerX);

        const item = {
          note: pitch,
          start: start,
          velocity: 100,
          duration: 0.25,
          label: "",
        };

        this._currentNote = this.add(new GridItem(this, item));
        this._currentNote.domElement.style.top = `${
          (87 - this._currentNote.note) * this.noteHeight
        }px`;
        this._currentNote.domElement.style.left = `${
          this._currentNote.start * this.beatWidth
        }px`;
        this._dragMode = "end";
      }

      this.emit("update", this);
    });

    this.gridElement.addEventListener("pointerup", () => {
      this.gridElement.classList.remove("dragging");
      this._currentNote = null;

      this.emit("update", this);
    });

    this.gridElement.addEventListener("pointerleave", () => {
      this.gridElement.classList.remove("dragging");
      if (this._currentNote) {
        this.remove(this._currentNote);
        this._currentNote = null;
      }
    });

    this.gridElement.addEventListener("contextmenu", (event) => {
      event.preventDefault();
    });

    this.gridElement.addEventListener("pointermove", (event) => {
      if (this._currentNote && event.buttons === 1) {
        if (this._dragMode === "start") {
          const oldStart = this._currentNote.start;
          this._currentNote.start = event.layerX / this.beatWidth;
          this._currentNote.start =
            Math.round(this._currentNote.start / this._quantize) *
            this._quantize;
          this._currentNote.duration =
            oldStart - this._currentNote.start + this._currentNote.duration;
          this._currentNote.domElement.style.left = `${
            this._currentNote.start * this.beatWidth
          }px`;
          this._currentNote.domElement.style.width = `${
            this._currentNote.duration * this.beatWidth
          }px`;
        } else if (this._dragMode === "end") {
          this._currentNote.duration =
            event.layerX / this.beatWidth - this._currentNote.start;

          // quantize
          this._currentNote.duration =
            Math.round(this._currentNote.duration / this._quantize) *
            this._quantize;

          this._currentNote.domElement.style.width = `${
            this._currentNote.duration * this.beatWidth
          }px`;
        } else if (this._dragMode === "move") {
          this._currentNote.start =
            (event.layerX - this._dragOffset) / this.beatWidth;
          this._currentNote.start =
            Math.round(this._currentNote.start / this._quantize) *
            this._quantize;
          this._currentNote.domElement.style.left = `${
            this._currentNote.start * this.beatWidth
          }px`;
        } else {
          return;
        }

        this.emit("update", this);
      }
    });

    this.gridElement.addEventListener("pointerup", () => {
      this.gridElement.classList.remove("dragging");
      if (this._currentNote) {
        this._currentNote.domElement.style.pointerEvents = "auto";
      }
      this._currentNote = null;
    });

    this.gridElement.addEventListener("pointerleave", () => {
      this.gridElement.classList.remove("dragging");
      if (this._currentNote) {
        this._currentNote.domElement.style.pointerEvents = "auto";
      }
      this._currentNote = null;
    });
  }

  add(event: GridItem) {
    if (!this._track) throw new Error("add() No track!");
    this._track.events.push(event);
    console.log("Grid: add", event);
    return event;
  }

  remove(event: GridItem) {
    if (!this._track) throw new Error("remove() No track!");
    this._track.events.splice(this._track.events.indexOf(event), 1);
    this.gridElement.removeChild(event.domElement);
  }

  load(track: PatternTrack) {
    console.log("Grid: load", track.events);
    this._track?.events.forEach((event) => event.domElement.remove());
    this._track = track;
    track.events.forEach((event) => {
      this.gridElement.appendChild(event.domElement);
    });
  }

  renderToCanvas(canvas: HTMLCanvasElement, color: string) {
    if (!this._track) throw new Error("renderToCanvas() No track!");

    // find lowest note
    let lowestNote = 88;
    this._track.events.forEach((note) => {
      if (note.note < lowestNote) lowestNote = note.note;
    });

    // find highest note
    let highestNote = 0;
    this._track.events.forEach((note) => {
      if (note.note > highestNote) highestNote = note.note;
    });

    highestNote += 12;
    lowestNote -= 12;

    const ctx = canvas.getContext("2d") as CanvasRenderingContext2D;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    let padded_scale = canvas.height / (highestNote - lowestNote + 1);

    if (padded_scale > 2) {
      padded_scale = 2;
    }

    this._track.events.forEach((note) => {
      const y = canvas.height - (note.note - lowestNote + 1) * padded_scale;
      const x = note.start * this.beatWidth;
      const width = note.duration * this.beatWidth;
      ctx.fillStyle = color;
      ctx.fillRect(x, y, width, padded_scale);
    });
  }
}