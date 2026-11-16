import * as THREE from "three";
import { RoundedBoxGeometry } from "three/addons/geometries/RoundedBoxGeometry.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

const reduceMotion = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
const perfLite = !!(connection && connection.saveData) || (navigator.deviceMemory && navigator.deviceMemory <= 2);

(function status() {
    function sarajevoNow() {
        return new Date(new Date().toLocaleString("en-US", { timeZone: "Europe/Sarajevo" }));
    }
    function update() {
        const now = sarajevoNow();
        const day = now.getDay();
        const mins = now.getHours() * 60 + now.getMinutes();
        const open = day >= 1 && day <= 6 && mins >= 600 && mins < 1080;
        let text;
        if (open) text = "Trenutno otvoreno · do 18:00";
        else if (day >= 1 && day <= 6 && mins < 600) text = "Trenutno zatvoreno · otvaramo danas u 10:00";
        else if (day === 6 || day === 0) text = "Trenutno zatvoreno · otvaramo u ponedjeljak u 10:00";
        else text = "Trenutno zatvoreno · otvaramo sutra u 10:00";
        document.querySelectorAll("[data-status]").forEach(function (el) {
            el.classList.toggle("closed", !open);
            const t = el.querySelector("[data-status-text]");
            if (t) t.textContent = text;
        });
        document.querySelectorAll(".hours-list p").forEach(function (p) {
            p.classList.toggle("today", parseInt(p.getAttribute("data-day"), 10) === day);
        });
    }
    update();
    setInterval(update, 60000);
})();

fetch("../rating.json", { cache: "no-store" }).then(function (r) { return r.json(); }).then(function (d) {
    if (!d) return;
    if (typeof d.count === "number") {
        document.querySelectorAll("[data-reviews]").forEach(function (el) { el.textContent = String(d.count); });
    }
}).catch(function () {});

const stops = ["Svijet", "Evropa", "Bosna i Hercegovina", "Goražde", "Auto Servis Šunja"];
const flight = document.getElementById("flightLabel");
const bar = document.getElementById("scrollBar");
const track = document.getElementById("serviceTrack");

if (window.gsap && window.ScrollTrigger && track && !reduceMotion) {
    gsap.registerPlugin(ScrollTrigger);
    gsap.to(track, {
        x: function () { return Math.min(0, window.innerWidth - track.scrollWidth - 48); },
        ease: "none",
        scrollTrigger: {
            trigger: "#usluge",
            start: "top top",
            end: "bottom bottom",
            scrub: 0.7
        }
    });
    document.querySelectorAll("[data-reveal]").forEach(function (el) {
        gsap.from(el, {
            y: 36,
            opacity: 0,
            duration: 0.7,
            ease: "power3.out",
            scrollTrigger: { trigger: el, start: "top 86%", once: true }
        });
    });
}

const canvas = document.getElementById("stage");
const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: !perfLite, alpha: true, powerPreference: "high-performance" });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, perfLite ? 1.25 : 1.6));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = !perfLite;

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x07090d, 9, 22);
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

const camera = new THREE.PerspectiveCamera(32, window.innerWidth / window.innerHeight, 0.1, 80);
camera.position.set(6.2, 1.7, 7.2);

scene.add(new THREE.HemisphereLight(0xd7e7ff, 0x1a120c, 0.7));
const key = new THREE.DirectionalLight(0xffffff, 2.4);
key.position.set(5, 8, 4);
key.castShadow = !perfLite;
scene.add(key);
const rim = new THREE.DirectionalLight(0x4ea8ff, 3.2);
rim.position.set(-6, 3, -4);
scene.add(rim);
const fill = new THREE.PointLight(0xfff1d6, 8, 16);
fill.position.set(2, 1.4, 3);
scene.add(fill);

const paint = new THREE.MeshPhysicalMaterial({
    color: 0x0c74c8,
    metalness: 0.82,
    roughness: 0.18,
    clearcoat: 1,
    clearcoatRoughness: 0.05,
    envMapIntensity: 1.5
});
const glassMat = new THREE.MeshPhysicalMaterial({
    color: 0x0a1622,
    metalness: 0.05,
    roughness: 0.04,
    transparent: true,
    opacity: 0.55,
    envMapIntensity: 1.6
});
const lamp = new THREE.MeshStandardMaterial({ color: 0xfff8ea, emissive: 0xfff3cf, emissiveIntensity: 2.4, roughness: 0.25 });
const tailMat = new THREE.MeshStandardMaterial({ color: 0xc81d1d, emissive: 0xff2a2a, emissiveIntensity: 1.8 });
const chrome = new THREE.MeshStandardMaterial({ color: 0xe6ebf1, metalness: 1, roughness: 0.18 });
const rubber = new THREE.MeshStandardMaterial({ color: 0x161616, roughness: 0.9 });

const profile = new THREE.Shape();
profile.moveTo(-2.05, 0.48);
profile.lineTo(1.55, 0.48);
profile.bezierCurveTo(2.2, 0.48, 2.25, 0.78, 2.02, 0.92);
profile.lineTo(1.2, 1.0);
profile.lineTo(0.48, 1.48);
profile.lineTo(-0.72, 1.52);
profile.lineTo(-1.28, 1.08);
profile.lineTo(-1.82, 0.96);
profile.bezierCurveTo(-2.22, 0.86, -2.25, 0.55, -2.05, 0.48);
const bodyGeo = new THREE.ExtrudeGeometry(profile, {
    depth: 1.48,
    bevelEnabled: true,
    bevelThickness: 0.07,
    bevelSize: 0.09,
    bevelSegments: 4,
    curveSegments: 16
});
bodyGeo.translate(0, 0, -0.74);
const car = new THREE.Group();
const body = new THREE.Mesh(bodyGeo, paint);
body.castShadow = true;
car.add(body);
function pane(w, h, x, y, z, rotZ) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), glassMat);
    m.position.set(x, y, z);
    m.rotation.z = rotZ;
    car.add(m);
}
pane(0.95, 0.48, 0.78, 1.22, 0.76, -0.72);
pane(0.95, 0.48, 0.78, 1.22, -0.76, -0.72);
pane(0.7, 0.42, -1.05, 1.22, 0.76, 0.55);
pane(0.7, 0.42, -1.05, 1.22, -0.76, 0.55);
function addBar(mat, w, h, d, x, y, z) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
    m.position.set(x, y, z);
    car.add(m);
}
addBar(lamp, 0.08, 0.1, 0.36, 2.08, 0.78, 0.48);
addBar(lamp, 0.08, 0.1, 0.36, 2.08, 0.78, -0.48);
addBar(tailMat, 0.08, 0.12, 0.42, -2.08, 0.86, 0.46);
addBar(tailMat, 0.08, 0.12, 0.42, -2.08, 0.86, -0.46);
addBar(new THREE.MeshStandardMaterial({ color: 0x0a0d12, roughness: 0.5 }), 0.06, 0.22, 0.7, 2.1, 0.7, 0);

const wheels = [];
function makeWheel(x, z) {
    const g = new THREE.Group();
    const tire = new THREE.Mesh(new THREE.CylinderGeometry(0.36, 0.36, 0.24, 28), rubber);
    tire.rotation.z = Math.PI / 2;
    const rim = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.26, 18), chrome);
    rim.rotation.z = Math.PI / 2;
    const spoke = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.04, 0.05), chrome);
    spoke.position.z = 0;
    g.add(tire, rim, spoke);
    g.position.set(x, 0.36, z);
    car.add(g);
    wheels.push(g);
}
makeWheel(1.32, 0.86);
makeWheel(1.32, -0.86);
makeWheel(-1.32, 0.86);
makeWheel(-1.32, -0.86);
scene.add(car);


const ground = new THREE.Mesh(
    new THREE.CircleGeometry(16, 48),
    new THREE.MeshStandardMaterial({ color: 0x10151c, metalness: 0.65, roughness: 0.42 })
);
ground.rotation.x = -Math.PI / 2;
ground.receiveShadow = true;
scene.add(ground);

let progress = 0;
function readProgress() {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    progress = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
    if (bar) bar.style.width = (progress * 100) + "%";
    const pin = document.getElementById("lokacija");
    if (flight && pin) {
        const r = pin.getBoundingClientRect();
        const local = 1 - Math.min(1, Math.max(0, (r.bottom) / (r.height + window.innerHeight)));
        const idx = Math.min(stops.length - 1, Math.floor(local * stops.length));
        if (r.top < window.innerHeight && r.bottom > 0) flight.textContent = stops[idx];
    }
}
window.addEventListener("scroll", readProgress, { passive: true });
readProgress();

let smooth = 0;
const clock = new THREE.Clock();
function frame() {
    requestAnimationFrame(frame);
    const dt = Math.min(0.05, clock.getDelta());
    smooth += (progress - smooth) * (reduceMotion ? 1 : 0.08);
    const p = smooth;
    const yaw = -0.55 + p * Math.PI * 1.65;
    const bob = reduceMotion ? 0 : Math.sin(clock.elapsedTime * 1.2) * 0.03;
    car.rotation.y = yaw;
    car.position.y = bob;
    const spin = reduceMotion ? 0 : p * 26;
    wheels.forEach(function (w) { w.rotation.x = spin; });
    const radius = 8.1 - Math.sin(p * Math.PI) * 1.8;
    const camY = 1.45 + Math.sin(p * Math.PI) * 1.05;
    camera.position.set(Math.sin(yaw + 0.9) * radius, camY, Math.cos(yaw + 0.9) * radius);
    camera.lookAt(0, 0.75, 0);
    rim.intensity = 2.2 + Math.sin(p * Math.PI) * 1.4;
    renderer.render(scene, camera);
}
frame();

window.addEventListener("resize", function () {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    if (window.ScrollTrigger) ScrollTrigger.refresh();
});
