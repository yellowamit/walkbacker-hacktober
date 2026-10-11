/**
 * WalkBacker Compass & Device Orientation Controller
 * Computes live compass dial rotation and points needle towards Trailhead Base.
 */
class CompassController {
  constructor() {
    this.deviceHeading = 0;       // User's current facing azimuth (0-360)
    this.targetBearing = 235;     // Required return bearing to origin (degrees)
    this.hasOrientationSensor = false;

    this.arrowElement = document.getElementById("compassArrow");
    this.pocketArrowElement = document.getElementById("pocketArrow");
    this.bearingHeadingElement = document.getElementById("bearingHeading");
    this.cardinalHeadingElement = document.getElementById("cardinalHeading");

    this.initSensor();
  }

  initSensor() {
    // Check for DeviceOrientation event support (iOS 13+ requires permission request on user action)
    if (window.DeviceOrientationEvent) {
      window.addEventListener("deviceorientationabsolute", (e) => this.handleOrientation(e), true);
      window.addEventListener("deviceorientation", (e) => this.handleOrientation(e), true);
    }
  }

  handleOrientation(event) {
    let compass = null;

    if (event.webkitCompassHeading !== undefined) {
      // iOS WebKit compass heading
      compass = event.webkitCompassHeading;
    } else if (event.alpha !== null) {
      // Android / W3C orientation
      compass = 360 - event.alpha;
    }

    if (compass !== null && !isNaN(compass)) {
      this.hasOrientationSensor = true;
      this.deviceHeading = compass;
      this.updateDial();
    }
  }

  setTargetBearing(bearingDeg) {
    this.targetBearing = (bearingDeg + 360) % 360;
    this.updateDial();
  }

  updateDial() {
    // Relative angle: target bearing relative to device heading
    const relativeAngle = (this.targetBearing - this.deviceHeading + 360) % 360;

    if (this.arrowElement) {
      this.arrowElement.style.transform = `rotate(${relativeAngle}deg)`;
    }
    if (this.pocketArrowElement) {
      this.pocketArrowElement.style.transform = `rotate(${relativeAngle}deg)`;
    }

    // Cardinal translation
    const cardinals = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"];
    const cardIdx = Math.round(this.targetBearing / 45) % 8;
    const cardinalStr = cardinals[cardIdx];

    if (this.bearingHeadingElement) {
      this.bearingHeadingElement.textContent = `${Math.round(this.targetBearing)}°`;
    }
    if (this.cardinalHeadingElement) {
      this.cardinalHeadingElement.textContent = cardinalStr;
    }

    const pocketBearing = document.getElementById("pocketBearing");
    if (pocketBearing) {
      pocketBearing.textContent = `${Math.round(this.targetBearing)}° ${cardinalStr}`;
    }
  }
}

// Global compass controller
window.compassController = new CompassController();
