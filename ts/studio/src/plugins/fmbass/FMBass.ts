import { Instrument } from "../../abstracts/Instrument";
import { InstrumentWindow } from "../../abstracts/InstrumentWindow";
import { SynthesizerVoice } from "../../abstracts/SynthesizerVoice";
import type { Mixer } from "../../elements/Mixer";
import type { AudioClock } from "../../elements/components/AudioClock";
import { Envelope } from "../../elements/components/Envelope";
import { Knob } from "../../elements/components/Knob";
import type { ISourceEvent } from "../../elements/components/SamplerSlot";
import { Slider } from "../../elements/components/Slider";
import type { ControllerGroup } from "../../schema";

function noteToFrequency(note: number) {
  return 440 * Math.pow(2, (note - 69) / 12);
}

export class FMBassVoice extends SynthesizerVoice {
  constructor(readonly audioClock: AudioClock) {
    super(audioClock);
  }

  trigger(note: number, when: number, velocity: number | undefined) {
    console.log("FMBassVoice triggered", note, when, velocity);
  }

  release(note: number) {
    console.log("FMBassVoice released", note);
  }
}

export class FMBass extends Instrument {
  readonly name = "FM Bass";
  readonly id = "fm_bass";
  readonly version = "0.0.1";
  readonly description = "A simple FM bass synthesizer";
  readonly author = "Johnny Street";
  readonly controllerGroups: ControllerGroup[] = [];
  readonly window: InstrumentWindow;
  private _carrier?: OscillatorNode;
  private _modulator?: OscillatorNode;
  readonly modulatorGain: GainNode;
  readonly filter: BiquadFilterNode;
  readonly gain: GainNode;
  readonly filterEnvelope: Envelope;
  readonly gainEnvelope: Envelope;
  private _heldNote: number | undefined;

  public fmRatio = 1;

  constructor(
    readonly audioClock: AudioClock,
    mixer: Mixer,
    mixerChannel = 0
  ) {
    super(audioClock, mixer);

    this.window = new InstrumentWindow(
      {
        title: "FM Bass",
        persistent: true,
        content: this.domElement,
        mixerChannel,
      },
      this
    );

    const audioContext = this.audioClock.audioContext;

    this.modulatorGain = audioContext.createGain();
    this.modulatorGain.gain.value = 100;

    this.gain = audioContext.createGain();
    this.gain.gain.value = 0;

    const highpassFilter = audioContext.createBiquadFilter();
    highpassFilter.type = "highpass";
    highpassFilter.frequency.value = 20;
    this.gain.connect(highpassFilter);
    highpassFilter.connect(this.output);

    this.output.gain.value = 0.5;

    this.filter = audioContext.createBiquadFilter();
    this.filter.type = "lowpass";
    this.filter.frequency.value = 440;
    this.filter.Q.value = 1;
    this.filter.connect(this.gain);

    this.filterEnvelope = new Envelope();
    this.gainEnvelope = new Envelope();

    const fmGainKnob = new Knob({
      controlType: "knob",
      name: "FM Gain",
      label: "FM Gain",
      min: 0,
      max: 300,
      step: 1,
      default: 100,
      value: 100,
    });

    this.window.content.appendChild(fmGainKnob.domElement);
    fmGainKnob.on("change", () => {
      console.log("FM Gain", fmGainKnob.value);
      this.modulatorGain.gain.value = fmGainKnob.value;
    });

    const fmRatioKnob = new Knob({
      controlType: "knob",
      name: "FM Ratio",
      label: "FM Ratio",
      min: 0,
      max: 12,
      step: 1,
      default: this.fmRatio,
      value: this.fmRatio,
    });
    fmRatioKnob.on("change", () => {
      console.log("FM Ratio", fmRatioKnob.value);
      this.fmRatio = fmRatioKnob.value;
    });
    this.window.content.appendChild(fmRatioKnob.domElement);
  }

  trigger(note: number, when: number, velocity = 1): ISourceEvent | undefined {
    console.log("FM Bass triggered", when);

    this._heldNote = note;

    note += this.transpose;

    if (this._carrier?.context.state === "running") {
      const g = this.gain.gain.value;
      this.gain.gain.cancelScheduledValues(when);
      this.gain.gain.setValueAtTime(g, when);
      this.gain.gain.setTargetAtTime(0.01, when, 0.01);

      try {
        this._carrier.stop(when + 0.02);
        this._modulator?.stop(when + 0.02);
      } catch (e) {
        console.error("Error stopping carrier/modulator", e);
      }
    }

    this._carrier = this.audioClock.audioContext.createOscillator();
    this._carrier.frequency.value = 220;

    this._modulator = this.audioClock.audioContext.createOscillator();
    this._modulator.frequency.value = 220;

    this._carrier.connect(this.gain);
    this._modulator.connect(this.modulatorGain);
    this.modulatorGain.connect(this._carrier.frequency);

    this._carrier.type = "sine";

    this._carrier.start(when);
    this._modulator.start(when);

    const freq = noteToFrequency(note);
    let time = when || this.audioClock.currentTime;

    this.gainEnvelope.trigger(this.gain.gain, time);

    const value = this._carrier.frequency.value;

    time += 0.001;

    this._carrier.frequency.cancelScheduledValues(time);
    this._modulator.frequency.cancelScheduledValues(time);

    this._carrier.frequency.setValueAtTime(value, time);
    this._modulator.frequency.setValueAtTime(value * this.fmRatio, time);

    this._carrier.frequency.setTargetAtTime(freq, time, 0.001);
    this._modulator.frequency.setTargetAtTime(freq * this.fmRatio, time, 0.001);
    //this.filterEnvelope.trigger(this.filter.frequency, time);

    return undefined;
  }

  release(note: number, when: number) {
    if (this._heldNote !== note) {
      return;
    }
    console.log("FM Bass released", note);
    const time = when || this.audioClock.currentTime;
    this.filterEnvelope.triggerRelease(this.filter.frequency, time);
    this.gainEnvelope.triggerRelease(this.gain.gain, time);
  }
}
