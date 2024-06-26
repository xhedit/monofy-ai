import { BaseElement } from "./BaseElement";

export class DialogPopup extends BaseElement<"result" | "cancel"> {  
  closeButton: HTMLButtonElement;
  okButton: HTMLButtonElement | undefined;
  cancelButton: HTMLButtonElement | undefined;

  get isVisibile() {
    return this.domElement.style.display !== "none";
  }

  constructor(
    private readonly ok: string | HTMLButtonElement = "OK",
    private readonly cancel: string | HTMLButtonElement = "Cancel"
  ) {
    super("div", "dialog-popup");

    this.closeButton = document.createElement("button");
    this.closeButton.classList.add("window-close-button");    
    this.domElement.appendChild(this.closeButton);
    this.closeButton.addEventListener("pointerdown", () => {
      this.domElement.style.display = "none";
    });

    if (ok instanceof HTMLButtonElement) {
      this.okButton = ok;
    } else if (ok) {
      this.okButton = document.createElement("button");
      this.okButton.textContent = ok;
      this.domElement.appendChild(this.okButton);
    }

    if (this.okButton) {
      this.okButton.addEventListener("click", () => {
        this.emit("result", this);
      });
    }

    if (cancel instanceof HTMLButtonElement) {
      this.cancelButton = cancel;
    } else if (cancel) {
      this.cancelButton = document.createElement("button");
      this.cancelButton.textContent = cancel;
      this.domElement.appendChild(this.cancelButton);
    }

    if (this.cancelButton) {
      this.cancelButton.addEventListener("click", () => {
        this.emit("cancel", this);
      });
    }
  }

  show(x: number, y: number, targetObject?: unknown) { /* eslint-disable-line @typescript-eslint/no-unused-vars */
    this.domElement.style.display = "block";
    this.domElement.style.left = `${x}px`;
    this.domElement.style.top = `${y}px`;
    this.domElement.parentElement?.appendChild(this.domElement);
  }

  hide() {
    this.domElement.style.display = "none";
  }
}
