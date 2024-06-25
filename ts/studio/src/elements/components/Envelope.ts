import { BaseElement } from "../../../../elements/src/elements/BaseElement";
import { PluginControl } from "../../abstracts/PluginControl";
import { IEnvelope } from "../../schema";
import { Slider } from "./Slider";

export class Envelope extends BaseElement<"update"> {
  readonly attack: PluginControl;
  readonly hold: PluginControl;
  readonly decay: PluginControl;
  readonly sustain: PluginControl;
  readonly release: PluginControl;

  constructor(
    readonly settings: IEnvelope = {
      attack: 0.003,
      hold: 0.0,
      decay: 2.0,
      sustain: 0.01,
      release: 0.05,
    }
  ) {
    super("div", "envelope");

    // "attack", "A", 0, 1, 0.01, attack
    this.attack = new Slider({
      controlType: "slider",
      name: "attack",
      label: "A",
      min: 0,
      max: 1,
      step: 0.01,
      value: settings.attack,
      default: settings.attack,
    });
    this.hold = new Slider({
      controlType: "slider",
      name: "hold",
      label: "H",
      min: 0,
      max: 1,
      step: 0.01,
      value: settings.hold,
      default: settings.hold,
    });
    this.decay = new Slider({
      controlType: "slider",
      name: "decay",
      label: "D",
      min: 0,
      max: 1,
      step: 0.01,
      value: settings.decay,
      default: settings.decay,
    });
    this.sustain = new Slider({
      controlType: "slider",
      name: "sustain",
      label: "S",
      min: 0,
      max: 1,
      step: 0.01,
      value: settings.sustain,
      default: settings.sustain,
    });
    this.release = new Slider({
      controlType: "slider",
      name: "release",
      label: "R",
      min: 0,
      max: 1,
      step: 0.01,
      value: settings.release,
      default: settings.release,
    });

    this.domElement.appendChild(this.attack.domElement);
    this.domElement.appendChild(this.decay.domElement);
    this.domElement.appendChild(this.sustain.domElement);
    this.domElement.appendChild(this.release.domElement);
  }

  trigger(param: AudioParam, when: number) {
    console.log("trigger @ " + when);
    const value = param.value;
    param.cancelScheduledValues(when);
    param.setValueAtTime(value, when);
    param.exponentialRampToValueAtTime(0.015, when);
    //param.setValueAtTime(0.015, when);
    param.linearRampToValueAtTime(1, when + this.settings.attack);
    //param.setValueAtTime(1, when + this.attack.value);
    param.exponentialRampToValueAtTime(
      this.settings.sustain,
      when + this.settings.attack + this.settings.decay
    );
  }

  triggerRelease(param: AudioParam, when: number) {
    console.log("triggerRelease @ " + when);
    param.setValueAtTime(param.value, when);
    param.setTargetAtTime(0.0001, when + 0.01, this.settings.release);
    param.cancelScheduledValues(when + 0.01 + this.settings.release);
  }
}
