let can = document.getElementById(`board`),
    ctx = can.getContext(`2d`),
    fps = 60;

let mx, my;

let current = ``,
    selection = null;

let playerLanded = false;

const width = 600,
    height = 600,
    all = [];

const xin = document.getElementById(`x-coor`),
    yin = document.getElementById(`y-coor`),
    win = document.getElementById(`o-width`),
    hin = document.getElementById(`o-height`),
    dinx = document.getElementById(`o-dirx`),
    diny = document.getElementById(`o-diry`),
    tin = document.getElementById(`o-type`),
    pin = document.getElementById(`o-power`);

xin.addEventListener(`input`, _ => {
    if (selection === null)
        return;

    selection.x = parseInt(xin.value);
});

yin.addEventListener(`input`, _ => {
    if (selection === null)
        return;

    selection.y = parseInt(yin.value);
});

win.addEventListener(`input`, _ => {
    if (selection === null)
        return;

    selection.width = parseInt(win.value);
});

hin.addEventListener(`input`, _ => {
    if (selection === null)
        return;

    selection.height = parseInt(hin.value);
});

dinx.addEventListener(`input`, _ => {
    if (selection === null)
        return;

    selection.dirx = parseInt(dinx.value);
});

diny.addEventListener(`input`, _ => {
    if (selection === null)
        return;

    selection.diry = parseInt(diny.value);
});

pin.addEventListener(`input`, _ => {
    if (selection === null)
        return;

    selection.pir = parseInt(pin.value);
});

window.addEventListener(`load`, _ => {
    can.width = 600;
    can.height = 600;

    setInterval(loop, 1000 / fps)
});

window.addEventListener(`keyup`, e => {
    if (e.key === `b`)
        current = `block`;
    else if (e.key === `d`)
        current = `door`;
    else if (e.key === `k`)
        current = `key`;
    else if (e.key === `r`)
        current = `rotator`;
    else if (e.key === `s`)
        current = `spikes`;
    else if (e.key === `Escape`)
        current = ``;
    else if (e.key === `j`)
        current = `springboard`;
    else if (e.key === `f`)
        current = `jet`;
    else if (e.key === `a`)
        current = `crossbow`;
    else if (e.key === `p`) {
        if (!playerLanded) {
            current = `player`;
            playerLanded = true;
        }
    } else if (e.key === `Delete`) {
        if (selection != null) {
            all.splice(all.indexOf(selection), 1);
            xin.value = ``;
            yin.value = ``;
            win.value = ``;
            hin.value = ``;
            tin.value = ``;
            dinx.value = ``;
            diny.value = ``;
            pin.value = ``;
        }
    }
});

can.addEventListener(`mousemove`, e => {
    mx = e.x;
    my = e.y;
});

can.addEventListener(`mousedown`, _ => {
    if (current != ``) {
        addObj();
        current = ``;
    }

    let b = false;
    for (let a of all) {
        if (a.isMouseIn()) {
            selection = a;
            current = ``;

            xin.value = a.x;
            yin.value = a.y;
            tin.value = a.type;
            win.value = a.width;
            hin.value = a.height;
            dinx.value = a.dirx;
            diny.value = a.diry;
            pin.value = a.power;

            b = true;
        }
    }

    if (!b) {
        selection = null;

        xin.value = ``;
        yin.value = ``;
        tin.value = ``;
        win.value = ``;
        hin.value = ``;
        dinx.value = ``;
        diny.value = ``;
        pin.value = ``;
    }
});

class Obj {
    constructor(x, y, t) {
        this.x = x;
        this.y = y;
        this.dirx = 0;
        this.diry = 0;
        this.type = t;
        this.power = 0;

        if (t === `door`) {
            this.width = 10;
            this.height = 100;
        } else if (t === `key` || t === `jet`) {
            this.width = 20;
            this.height = 20;
        } else if (t === `rotator`) {
            this.width = 20;
            this.height = 20;
            this.dir = 1;
        } else if (t === `player`) {
            this.width = 40;
            this.height = 40;
        } else if (t === `spikes`) {
            this.width = 100;
            this.height = 10;
            this.dirx = -1;
        } else if (t === `springboard`) {
            this.width = 80;
            this.height = 10;
            this.power = -15;
        } else if (t === `crossbow`) {
            this.width = 40;
            this.height = 30;
            this.dirx = 1;
        } else {
            this.width = 50;
            this.height = 50;
        }
    }

    isMouseIn() {
        return mx >= this.x &&
            mx <= this.x + this.width &&
            my >= this.y &&
            my <= this.y + this.height;
    }
}

function addObj() {
    let o = new Obj(mx, my, current);
    all.push(o);
}

function loop() {
    update();
    render();
}

function update() {
}

function render() {
    ctx.clearRect(0, 0, width, height);

    ctx.fillStyle = `rgba(200, 200, 200, 1)`;
    ctx.fillRect(0, 0, width, height);

    renderGhost();

    for (let i of all) {
        renderObj(i);
    }
}

function renderGhost() {
    if (current === `block`) {
        ctx.fillStyle = `rgba(100, 100, 100, 1)`;
        ctx.strokeStyle = `rgba(0, 0, 0, 1)`;
        ctx.fillRect(mx, my, 50, 50);
        ctx.strokeRect(mx, my, 50, 50);
    } else if (current === `door`) {
        ctx.fillStyle = `rgba(100, 50, 50, 1)`;
        ctx.strokeStyle = `rgba(0, 0, 0, 1)`;
        ctx.fillRect(mx, my, 10, 100);
        ctx.strokeRect(mx, my, 10, 100);
    } else if (current === `key`) {
        ctx.fillStyle = `rgba(190, 190, 50, 1)`;
        ctx.strokeStyle = `rgba(0, 0, 0, 1)`;
        ctx.fillRect(mx, my, 20, 20);
        ctx.strokeRect(mx, my, 20, 20);
    } else if (current === `player`) {
        ctx.fillStyle = `rgba(200, 0, 0, 1)`;
        ctx.strokeStyle = `rgba(0, 0, 0, 1)`;
        ctx.fillRect(mx, my, 40, 40);
        ctx.strokeRect(mx, my, 40, 40);
    } else if (current === `rotator`) {
        ctx.fillStyle = `rgba(70, 130, 20, 1)`;
        ctx.strokeStyle = `rgba(0, 0, 0, 1)`;
        ctx.fillRect(mx, my, 20, 20);
        ctx.strokeRect(mx, my, 20, 20);
    } else if (current === `spikes`) {
        ctx.fillStyle = `rgba(50, 50, 50, 1)`;
        ctx.strokeStyle = `rgba(0, 0, 0, 1)`;

        for (let x = mx; x < mx + 100; x += 10) {
            ctx.beginPath();
            ctx.moveTo(x, my);
            ctx.lineTo(x + 5, my - 10);
            ctx.lineTo(x + 10, my);
            ctx.closePath();

            ctx.fill();
            ctx.stroke();
        }
    } else if (current === `springboard`) {
        ctx.fillStyle = `rgba(80, 20, 20, 1)`;
        ctx.strokeStyle = `rgba(0, 0, 0, 1)`;
        ctx.fillRect(mx, my, 80, 10);
        ctx.strokeRect(mx, my, 80, 10);

        ctx.fillStyle = `rgba(70, 70, 70, 1)`;
        ctx.fillRect(mx + 30, my + 10, 20, 10);
        ctx.strokeRect(mx + 30, my + 10, 20, 10);
    } else if (current === `jet`) {
        ctx.fillStyle = `rgba(140, 5, 180, 1)`;
        ctx.strokeStyle = `rgba(0, 0, 0, 1)`;
        ctx.fillRect(mx, my, 20, 20);
        ctx.strokeRect(mx, my, 20, 20);
    } else if (current === `crossbow`) {
        ctx.fillStyle = `rgba(100, 50, 0, 1)`;
        ctx.strokeStyle = `rgba(0, 0, 0, 1)`;
        ctx.fillRect(mx, my, 40, 10);
        ctx.strokeRect(mx, my, 40, 10);
        ctx.fillRect(mx, my + 20, 40, 10);
        ctx.strokeRect(mx, my + 20, 40, 10);
        ctx.fillRect(mx, my + 10, 10, 10);
        ctx.strokeRect(mx, my + 10, 10, 10);
    }

    if (current != ``) {
        ctx.font = `11px consolas`;
        ctx.fillStyle = `rgba(0, 0, 0, 1)`;
        ctx.textAlign = `center`;
        ctx.fillText(`(${mx}, ${my})`, mx, my - 10);
    } else {
        ctx.font = `11px consolas`;
        ctx.fillStyle = `rgba(0, 0, 0, 1)`;
        ctx.textAlign = `center`;
        ctx.fillText(`(${mx}, ${my})`, mx + 10, my + 30);
    }
}

function renderObj(o) {
    if (o.type === `block`) {
        ctx.fillStyle = `rgba(100, 100, 100, 1)`;
        ctx.strokeStyle = `rgba(0, 0, 0, 1)`;
        ctx.fillRect(o.x, o.y, o.width, o.height);
        ctx.strokeRect(o.x, o.y, o.width, o.height);
    } else if (o.type === `door`) {
        ctx.fillStyle = `rgba(100, 50, 50, 1)`;
        ctx.strokeStyle = `rgba(0, 0, 0, 1)`;
        ctx.fillRect(o.x, o.y, o.width, o.height);
        ctx.strokeRect(o.x, o.y, o.width, o.height);
    } else if (o.type === `key`) {
        ctx.fillStyle = `rgba(190, 190, 50, 1)`;
        ctx.strokeStyle = `rgba(0, 0, 0, 1)`;
        ctx.fillRect(o.x, o.y, o.width, o.height);
        ctx.strokeRect(o.x, o.y, o.width, o.height);
    } else if (o.type === `player`) {
        ctx.fillStyle = `rgba(200, 0, 0, 1)`;
        ctx.strokeStyle = `rgba(0, 0, 0, 1)`;
        ctx.fillRect(o.x, o.y, o.width, o.height);
        ctx.strokeRect(o.x, o.y, o.width, o.height);
    } else if (o.type === `rotator`) {
        ctx.fillStyle = `rgba(70, 130, 20, 1)`;
        ctx.strokeStyle = `rgba(0, 0, 0, 1)`;
        ctx.fillRect(o.x, o.y, o.width, o.height);
        ctx.strokeRect(o.x, o.y, o.width, o.height);
    } else if (o.type === `springboard`) {
        ctx.fillStyle = `rgba(80, 20, 20, 1)`;
        ctx.strokeStyle = `rgba(0, 0, 0, 1)`;
        ctx.fillRect(o.x, o.y, 80, 10);
        ctx.strokeRect(o.x, o.y, 80, 10);

        ctx.fillStyle = `rgba(70, 70, 70, 1)`;
        ctx.fillRect(o.x + 30, o.y + 10, 20, 10);
        ctx.strokeRect(o.x + 30, o.y + 10, 20, 10);
    } else if (o.type === `spikes`) {
        ctx.fillStyle = `rgba(50, 50, 50, 1)`;
        ctx.strokeStyle = `rgba(0, 0, 0, 1)`;

        let points = [];
        if (o.width > o.height) {
            for (let x = o.x; x < o.x + o.width; x += 10) {
                if (o.dirx === 1) {
                    points = [[x, o.y], [x + 5, o.y + o.height], [x + 10, o.y]];
                } else {
                    let y = o.y + o.height;
                    points = [[x, y], [x + 5, y - o.height], [x + 10, y]];
                }

                ctx.beginPath();
                ctx.moveTo(points[0][0], points[0][1]);
                ctx.lineTo(points[1][0], points[1][1]);
                ctx.lineTo(points[2][0], points[2][1]);
                ctx.closePath();

                ctx.fill();
                ctx.stroke();
            }
        } else {
            for (let y = o.y; y < o.y + o.height; y += 10) {
                if (o.dirx === 1) {
                    points = [[o.x, y], [o.x + o.width, y + 5], [o.x, y + 10]];
                } else {
                    let x = o.x + o.width;
                    points = [[x, y], [x - o.width, y + 5], [x, y + 10]];
                }

                ctx.beginPath();
                ctx.moveTo(points[0][0], points[0][1]);
                ctx.lineTo(points[1][0], points[1][1]);
                ctx.lineTo(points[2][0], points[2][1]);
                ctx.closePath();

                ctx.fill();
                ctx.stroke();
            }
        }
    } else if (o.type === `jet`) {
        ctx.fillStyle = `rgba(140, 5, 180, 1)`;
        ctx.strokeStyle = `rgba(0, 0, 0, 1)`;
        ctx.fillRect(o.x, o.y, 20, 20);
        ctx.strokeRect(o.x, o.y, 20, 20);
    } else if (o.type === `crossbow`) {
        ctx.fillStyle = `rgba(100, 50, 0, 1)`;
        ctx.strokeStyle = `rgba(0, 0, 0, 1)`;

        if (o.dirx > 0) {
            ctx.fillRect(o.x, o.y, 40, 10);
            ctx.strokeRect(o.x, o.y, 40, 10);
            ctx.fillRect(o.x, o.y + 20, 40, 10);
            ctx.strokeRect(o.x, o.y + 20, 40, 10);
            ctx.fillRect(o.x, o.y + 10, 10, 10);
            ctx.strokeRect(o.x, o.y + 10, 10, 10);
        } else if (o.dirx < 0) {
            ctx.fillRect(o.x, o.y, 40, 10);
            ctx.strokeRect(o.x, o.y, 40, 10);
            ctx.fillRect(o.x, o.y + 20, 40, 10);
            ctx.strokeRect(o.x, o.y + 20, 40, 10);
            ctx.fillRect(o.x + 30, o.y + 10, 10, 10);
            ctx.strokeRect(o.x + 30, o.y + 10, 10, 10);
        } else if (o.diry > 0) {
            ctx.fillRect(o.x, o.y, 10, 40);
            ctx.strokeRect(o.x, o.y, 10, 40);
            ctx.fillRect(o.x + 20, o.y, 10, 40);
            ctx.strokeRect(o.x + 20, o.y, 10, 40);
            ctx.fillRect(o.x + 10, o.y, 10, 10);
            ctx.strokeRect(o.x + 10, o.y, 10, 10);
        } else if (o.diry < 0) {
            ctx.fillRect(o.x, o.y, 10, 40);
            ctx.strokeRect(o.x, o.y, 10, 40);
            ctx.fillRect(o.x + 20, o.y, 10, 40);
            ctx.strokeRect(o.x + 20, o.y, 10, 40);
            ctx.fillRect(o.x + 10, o.y + 30, 10, 10);
            ctx.strokeRect(o.x + 10, o.y + 30, 10, 10);
        }
    }
}

function generate() {
    let str = `level = (\n`;
    let startPoint = {};

    for (let o of all) {
        if (o.type === `block`)
            str += `    game_objects.Block(${o.x}, ${o.y}, ${o.width}, ${o.height}),\n`;
        else if (o.type === `player`)
            startPoint = { x: o.x, y: o.y };
        else if (o.type === `door`)
            str += `    game_objects.Door(${o.x}, ${o.y}),\n`;
        else if (o.type === `key`)
            str += `    power_ups.Key(${o.x}, ${o.y}),\n`;
        else if (o.type === `rotator`)
            str += `    power_ups.GravityRotator(${o.x}, ${o.y}, ${o.dir}),\n`;
        else if (o.type === `jet`)
            str += `    power_ups.Jet(${o.x}, ${o.y}),\n`;
        else if (o.type === `spikes`)
            str += `    obstacles.Spikes(${o.x}, ${o.y}, ${o.width}, ${o.height}, ${o.dirx}),\n`;
        else if (o.type === `crossbow`)
            str += `    obstacles.Crossbow(${o.x}, ${o.y}, ${o.dirx}, ${o.diry}),\n`;
        else if (o.type === `springboard`)
            str += `    game_objects.SpringBoard(${o.x}, ${o.y}),\n`;
    }

    str = str.substring(0, str.length - 2);
    str += `\n)\n`;

    str += `Game.new_start_point(${startPoint.x}, ${startPoint.y})\n`;
    str += `Game.add_level(level)\n`;

    console.log(str);
}
