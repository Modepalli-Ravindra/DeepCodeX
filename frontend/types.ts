export interface User {
  id: string;
  name: string;
  email: string;
}

export enum ComplexityLevel {
  Low = "Low",
  Medium = "Medium",
  High = "High",
}

export interface AnalysisMetrics {
  linesOfCode: number;
  functionCount: number;
  loopCount: number;
  conditionalCount: number;
  cyclomaticComplexity: number;
}

export interface AnalysisResult {
  id?: string;                // optional (backend may not send)
  timestamp?: string;         // optional
  fileName?: string;          // optional

  language: string;
  isCode?: boolean;           // false if plain text detected
  message?: string;           // message when no code detected
  engine?: string;            // AST + CodeBERT + LLM
  complexityLevel: ComplexityLevel;

  score: number;              // 0–100
  optimizationPercentage: number; // 0–100
  refactorPercentage?: number; // 0-100

  timeComplexity: string;     // e.g., O(n)
  spaceComplexity: string;    // e.g., O(1)

  semanticConfidence?: number; // 0.0 – 1.0 (CodeBERT)

  metrics: AnalysisMetrics;
  suggestions: string[];
}

export interface ChartDataPoint {
  name: string;
  value: number;
}
