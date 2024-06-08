import { BaseElement } from "../../../../elements/src/elements/BaseElement";
import { IPlaylistEvent, IPlaylistItem, IPlaylistTrack } from "../../schema";

export class PlaylistTrack
  extends BaseElement<"update">
  implements IPlaylistTrack
{
  name = "Track 1";
  readonly items: IPlaylistItem[] = [];
  readonly events: IPlaylistEvent[] = [];
  readonly timeline: HTMLElement;

  constructor(name: string, events?: IPlaylistEvent[]) {
    super("div", "playlist-track");

    const settings = document.createElement("div");
    settings.classList.add("playlist-track-panel");

    const label = document.createElement("div");
    settings.appendChild(label);
    label.textContent = name;

    const buttons = document.createElement("div");
    buttons.classList.add("playlist-track-buttons");
    settings.appendChild(buttons);

    const mute = document.createElement("div");
    mute.classList.add("track-button");
    mute.classList.add("track-mute-button");
    mute.textContent = "M";
    mute.addEventListener("pointerdown", () => {
      mute.classList.toggle("active");
    });
    buttons.appendChild(mute);

    const solo = document.createElement("div");
    solo.classList.add("track-button");
    solo.classList.add("track-solo-button");
    solo.textContent = "S";
    solo.addEventListener("pointerdown", () => {
      solo.classList.toggle("active");
    });
    buttons.appendChild(solo);

    this.timeline = document.createElement("div");
    this.timeline.classList.add("playlist-track-timeline");

    this.timeline.addEventListener("pointerdown", (e) => {
      const x = e.offsetX;
      const duration = 1;
      const start = x / this.timeline.clientWidth;
      const label = "Event";

      const event: IPlaylistEvent = {
        start,
        duration,
        label,
        type: "pattern",
        value: {
          name: "Pattern",
          sequences: [],
        },
      };

      this.addEvent(event);
    });

    if (events) {
      this.loadEvents(events);
    }

    this.domElement.appendChild(settings);
    this.domElement.appendChild(this.timeline);
  }

  loadEvents(events: IPlaylistEvent[]) {
    for (const event of events) {
      this.addEvent(event);
    }
  }

  addEvent(event: IPlaylistEvent) {
    this.events.push(event);

    const item = document.createElement("div");
    item.classList.add("playlist-track-item");
    item.textContent = event.label;
    item.style.left = `${event.start * 100}px`;
    item.style.width = `${event.duration * 100}px`;

    this.timeline.appendChild(item);
  }
}
