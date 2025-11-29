
export type TimePoint = {
    t: number;
    y: number;
};

export type TimeSeries = TimePoint[];

export type DenseLinesOptions = {
    tMin?: number;
    tMax?: number;
    yMin?: number;
    yMax?: number;
    widthBins: number;
    heightBins: number;
};

export type DenseLinesResult = {
    grid: number[][];
    tMin: number;
    tMax: number;
    yMin: number;
    yMax: number;
    widthBins: number;
    heightBins: number;
};

export function computeDenseLines(
    seriesList: TimeSeries[],
    options: DenseLinesOptions,
): DenseLinesResult {
    const allT = seriesList.flatMap(s => s.map(p => p.t));
    const allY = seriesList.flatMap(s => s.map(p => p.y));

    const tMin = options.tMin ?? Math.min(...allT);
    const tMax = options.tMax ?? Math.max(...allT);
    const yMin = options.yMin ?? Math.min(...allY);
    const yMax = options.yMax ?? Math.max(...allY);

    const { widthBins, heightBins } = options;
    const grid: number[][] = Array(heightBins)
        .fill(0)
        .map(() => Array(widthBins).fill(0));

    const tRange = tMax - tMin;
    const yRange = yMax - yMin;

    for (const series of seriesList) {
        for (let i = 0; i < series.length - 1; i++) {
            const p1 = series[i];
            const p2 = series[i + 1];

            const t1 = (p1.t - tMin) / tRange;
            const y1 = (p1.y - yMin) / yRange;
            const t2 = (p2.t - tMin) / tRange;
            const y2 = (p2.y - yMin) / yRange;

            const x1 = Math.floor(t1 * (widthBins - 1));
            const y1_ = Math.floor((1 - y1) * (heightBins - 1));
            const x2 = Math.floor(t2 * (widthBins - 1));
            const y2_ = Math.floor((1 - y2) * (heightBins - 1));
            
            bresenhamLine(x1, y1_, x2, y2_, (x, y) => {
                if (x >= 0 && x < widthBins && y >= 0 && y < heightBins) {
                    grid[y][x]++;
                }
            });
        }
    }

    return { grid, tMin, tMax, yMin, yMax, widthBins, heightBins };
}

function bresenhamLine(
    x1: number,
    y1: number,
    x2: number,
    y2: number,
    callback: (x: number, y: number) => void,
) {
    let dx = Math.abs(x2 - x1);
    let dy = Math.abs(y2 - y1);
    let sx = x1 < x2 ? 1 : -1;
    let sy = y1 < y2 ? 1 : -1;
    let err = dx - dy;

    while (true) {
        callback(x1, y1);
        if (x1 === x2 && y1 === y2) break;
        let e2 = 2 * err;
        if (e2 > -dy) {
            err -= dy;
            x1 += sx;
        }
        if (e2 < dx) {
            err += dx;
            y1 += sy;
        }
    }
}

export function renderDenseLinesToCanvas(
    result: DenseLinesResult,
    canvas: HTMLCanvasElement,
) {
    const { grid, widthBins, heightBins } = result;
    canvas.width = widthBins;
    canvas.height = heightBins;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const maxDensity = Math.max(...grid.flatMap(row => row));
    if (maxDensity === 0) {
        ctx.fillStyle = "black";
        ctx.fillRect(0, 0, widthBins, heightBins);
        return;
    }

    const imageData = ctx.createImageData(widthBins, heightBins);
    for (let y = 0; y < heightBins; y++) {
        for (let x = 0; x < widthBins; x++) {
            const density = grid[y][x];
            const intensity = Math.floor((density / maxDensity) * 255);
            const index = (y * widthBins + x) * 4;
            imageData.data[index] = intensity; 
            imageData.data[index + 1] = intensity; 
            imageData.data[index + 2] = intensity; 
            imageData.data[index + 3] = 255;
        }
    }
    ctx.putImageData(imageData, 0, 0);
}
