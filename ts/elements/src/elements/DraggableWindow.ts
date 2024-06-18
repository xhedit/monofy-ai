import { EventDataMap } from "../EventObject";
import { SizableElement } from "./SizableElement";

export interface IWindowOptions {
  title: string;
  content?: HTMLElement;
  persistent?: boolean;
  width?: number;
  height?: number;
  top?: number;
  left?: number;
}

export class DraggableWindow<
  T extends keyof EventDataMap = keyof EventDataMap,
> extends SizableElement<"update" | "resize" | "open" | "close" | T> {
  readonly titlebar: HTMLElement;
  readonly content: HTMLElement;
  private readonly persistent;
  private readonly _title: HTMLElement;
  private readonly _closeButton: HTMLButtonElement;
  private _isDragging = false;
  private _dragOffsetX = 0;
  private _dragOffsetY = 0;
  private _top = 0;
  private _left = 0;

  get isVisible() {
    return this.domElement.style.display !== "none";
  }

  constructor(options: IWindowOptions) {
    super("div", "draggable-window");

    this.domElement.style.display = "none";

    this._top = options.top || 0;
    this._left = options.left || 0;

    this.persistent = options.persistent || false;

    this.titlebar = document.createElement("div");
    this.titlebar.className = "window-titlebar";
    this.domElement.appendChild(this.titlebar);

    this.titlebar.addEventListener("pointerdown", (e) => {
      this._isDragging = true;
      this._dragOffsetX =
        e.clientX - this.domElement.getBoundingClientRect().left;
      this._dragOffsetY =
        e.clientY -
        this.domElement.getBoundingClientRect().top +
        this.domElement.parentElement!.getBoundingClientRect().top +
        this.domElement.parentElement!.scrollTop;

      const ondrag = (e: PointerEvent) => {
        if (this._isDragging) {
          console.log("Dragging");

          let newTop = e.clientY - this._dragOffsetY;
          let newLeft = e.clientX - this._dragOffsetX;

          if (newTop < 0) {
            newTop = 0;
          }

          if (newLeft < 0) {
            newLeft = 0;
          }

          this.domElement.style.top = `${newTop}px`;
          this.domElement.style.left = `${newLeft}px`;

          this._top = newTop;
          this._left = newLeft;
        }
      };

      const onrelease = () => {
        this._isDragging = false;
        document.body.removeEventListener("pointermove", ondrag);
        document.body.removeEventListener("pointerup", onrelease);
      };

      document.body.addEventListener("pointermove", ondrag);
      document.body.addEventListener("pointerup", onrelease);
    });

    this._title = document.createElement("div");
    this._title.className = "window-titlebar-title";
    this._title.textContent = options.title;
    this.titlebar.appendChild(this._title);

    this.content = document.createElement("div");
    this.content.className = "window-content";
    this.domElement.appendChild(this.content);

    this._closeButton = document.createElement("button");
    this._closeButton.className = "window-close-button";
    this._closeButton.addEventListener("pointerdown", (e) => {
      if (e.button === 0) this.close();
    });

    this.titlebar.appendChild(this._closeButton);

    const width = options.width || 640;
    const height = options.height || 400;
    this.setSize(width, height);

    if (options.content) this.content.appendChild(options.content);
  }

  show(x?: number, y?: number) {
    if (x === undefined) x = this._left;
    if (y === undefined) y = this._top;

    this._top = y;
    this._left = x;

    if (this._top === 0 && this._left === 0) {
      x = window.innerWidth / 2 - 200;
      y = window.innerHeight / 4;
    }

    this.domElement.style.display = "flex";
    this.domElement.style.top = `${y}px`;
    this.domElement.style.left = `${x}px`;

    setTimeout(() => {
      this.domElement.parentElement?.appendChild(this.domElement);
      this.emit("open");
    }, 1);
  }

  close() {
    this.domElement.style.display = "none";
    this.emit("close");
    if (!this.persistent) {
      console.log("Removing window", this);
      this.domElement.remove();
    }
  }

  setSize(width: number, height: number) {
    this.domElement.style.width = `${width}px`;
    this.domElement.style.height = `${height}px`;
  }

  setPosition(x: number, y: number) {
    this.domElement.style.top = `${y}px`;
    this.domElement.style.left = `${x}px`;
  }

  setTitle(title: string) {
    this._title.textContent = title;
  }
}
