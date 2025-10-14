import { Button } from "@/components/ui/button";
import {
  CloudSun,
  Wheat,
  Banknote,
  Calendar,
  Search,
  Calculator,
  Droplets,
  Bug,
} from "lucide-react";

interface SuggestionQueriesProps {
  onQueryClick: (query: string) => void;
}

export function SuggestionQueries({ onQueryClick }: SuggestionQueriesProps) {
  const calculatorQueries = [
    "Calculate fertilizer for 3 acres of wheat with soil nitrogen 15 ppm",
    "How much seed needed for 2 acres of cotton with 45cm spacing?",
    "Daily water requirement for 1 acre rice using drip irrigation",
    "Mix chlorpyrifos at 2ml/L for 100 liter tank",
    "Profit calculation for wheat: ₹25000 costs, 30 quintal yield, ₹2200 price",
  ];

  const farmingQueries = [
    "Best crops for monsoon season in Punjab",
    "Weather forecast for Delhi this week",
    "PM Kisan scheme eligibility and benefits",
    "Cotton pest management techniques",
    "Current wheat prices in APMC mandis",
    "When to harvest sugarcane crop?",
    "Organic farming certification process",
    "Drip irrigation setup cost and benefits",
  ];

  const categories = [
    {
      icon: Calculator,
      name: "Calculators",
      query: "Show me farming calculators",
    },
    {
      icon: CloudSun,
      name: "Weather",
      query: "What's the weather forecast?",
    },
    {
      icon: Wheat,
      name: "Crops",
      query: "Best crops to grow in current season",
    },
    {
      icon: Banknote,
      name: "Schemes",
      query: "Government schemes for farmers",
    },
    {
      icon: Droplets,
      name: "Irrigation",
      query: "Irrigation planning and water management",
    },
    {
      icon: Bug,
      name: "Pest Control",
      query: "Pest and disease management",
    },
    {
      icon: Calendar,
      name: "Calendar",
      query: "Crop calendar for my region",
    },
    {
      icon: Search,
      name: "Market",
      query: "Current market prices",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center space-y-3">
        <h1 className="text-3xl font-bold text-primary">Kheti 🌾</h1>
        <p className="text-muted-foreground text-lg">
          Your AI assistant for agriculture in India
        </p>
      </div>

      {/* Quick Categories */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-4 gap-3">
        {categories.map((category, index) => (
          <Button
            key={index}
            variant="outline"
            className="h-20 flex-col gap-2 transition-all duration-200 hover:bg-accent"
            onClick={() => onQueryClick(category.query)}
          >
            <category.icon className="h-5 w-5 text-primary" />
            <span className="text-xs font-medium">{category.name}</span>
          </Button>
        ))}
      </div>

      {/* Calculator Questions */}
      <div className="space-y-4">
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide flex items-center gap-2">
          <Calculator className="h-4 w-4" />
          Calculator Tools
        </h3>
        <div className="grid gap-2">
          {calculatorQueries.map((query, index) => (
            <Button
              key={index}
              variant="ghost"
              className="h-auto py-3 px-4 text-left justify-start hover:bg-accent rounded-lg"
              onClick={() => onQueryClick(query)}
            >
              <div className="flex items-center gap-3 w-full">
                <div className="w-2 h-2 rounded-full bg-primary flex-shrink-0" />
                <span className="text-sm text-foreground">{query}</span>
              </div>
            </Button>
          ))}
        </div>
      </div>

      {/* Farming Questions */}
      <div className="space-y-4">
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide flex items-center gap-2">
          <Wheat className="h-4 w-4" />
          Popular Questions
        </h3>
        <div className="grid gap-2">
          {farmingQueries.map((query, index) => (
            <Button
              key={index}
              variant="ghost"
              className="h-auto py-3 px-4 text-left justify-start hover:bg-accent rounded-lg"
              onClick={() => onQueryClick(query)}
            >
              <div className="flex items-center gap-3 w-full">
                <div className="w-2 h-2 rounded-full bg-primary flex-shrink-0" />
                <span className="text-sm text-foreground">{query}</span>
              </div>
            </Button>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="text-center pt-4">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent border border-border">
          <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
          <span className="text-xs text-muted-foreground">
            Specialized for Indian agriculture • 12 tools available
          </span>
        </div>
      </div>
    </div>
  );
}
