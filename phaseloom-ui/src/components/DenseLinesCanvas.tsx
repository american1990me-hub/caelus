import React, { useEffect, useRef } from "react";
import { computeDenseLines, renderDenseLinesToCanvas, TimeSeries } from "./denselines";

interface Props {
  seriesList: TimeSeries[];
  widthBins?: number;
  heightBins?: number;
}

export const DenseLinesCanvas: React.FC<Props> = ({
  seriesList,
  widthBins = 400,
  heightBins = 200,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    if (!canvasRef.current || seriesList.length === 0) return;

    const allT = seriesList.flatMap((s) => s.map((p) => p.t));
    const allY = seriesList.flatMap((s) => s.map((p) => p.y));
    const tMin = Math.min(...allT);
    const tMax = Math.max(...allT);
    const yMin = Math.min(...allY);
    const yMax = Math.max(...allY);

    const result = computeDenseLines(seriesList, {
      widthBins,
      heightBins,
      tMin,
      tMax,
      yMin,
      yMax,
    });
    renderDenseLinesToCanvas(result, canvasRef.current);
  }, [seriesList, widthBins, heightBins]);

  return <canvas ref={canvasRef} style={{ width: "100%", height: "200px", display: "block" }} />;
};
