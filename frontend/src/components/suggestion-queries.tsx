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
      color: "text-blue-600",
      bgColor: "hover:bg-blue-50 dark:hover:bg-blue-950",
    },
    {
      icon: CloudSun,
      name: "Weather",
      query: "What's the weather forecast?",
      color: "text-orange-600",
      bgColor: "hover:bg-orange-50 dark:hover:bg-orange-950",
    },
    {
      icon: Wheat,
      name: "Crops",
      query: "Best crops to grow in current season",
      color: "text-green-600",
      bgColor: "hover:bg-green-50 dark:hover:bg-green-950",
    },
    {
      icon: Banknote,
      name: "Schemes",
      query: "Government schemes for farmers",
      color: "text-purple-600",
      bgColor: "hover:bg-purple-50 dark:hover:bg-purple-950",
    },
    {
      icon: Droplets,
      name: "Irrigation",
      query: "Irrigation planning and water management",
      color: "text-cyan-600",
      bgColor: "hover:bg-cyan-50 dark:hover:bg-cyan-950",
    },
    {
      icon: Bug,
      name: "Pest Control",
      query: "Pest and disease management",
      color: "text-red-600",
      bgColor: "hover:bg-red-50 dark:hover:bg-red-950",
    },
    {
      icon: Calendar,
      name: "Calendar",
      query: "Crop calendar for my region",
      color: "text-indigo-600",
      bgColor: "hover:bg-indigo-50 dark:hover:bg-indigo-950",
    },
    {
      icon: Search,
      name: "Market",
      query: "Current market prices",
      color: "text-emerald-600",
      bgColor: "hover:bg-emerald-50 dark:hover:bg-emerald-950",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center space-y-3">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
          Kheti 🌾
        </h1>
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
            className={`h-20 flex-col gap-2 ${category.bgColor} border-border transition-all duration-200 hover:scale-105`}
            onClick={() => onQueryClick(category.query)}
          >
            <category.icon className={`h-5 w-5 ${category.color}`} />
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
              className="h-auto py-3 px-4 text-left justify-start hover:bg-blue-50 dark:hover:bg-blue-950 rounded-xl"
              onClick={() => onQueryClick(query)}
            >
              <div className="flex items-center gap-3 w-full">
                <div className="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0" />
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
              className="h-auto py-3 px-4 text-left justify-start hover:bg-green-50 dark:hover:bg-green-950 rounded-xl"
              onClick={() => onQueryClick(query)}
            >
              <div className="flex items-center gap-3 w-full">
                <div className="w-2 h-2 rounded-full bg-green-500 flex-shrink-0" />
                <span className="text-sm text-foreground">{query}</span>
              </div>
            </Button>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="text-center pt-4">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span className="text-xs text-green-700 dark:text-green-300">
            Specialized for Indian agriculture • 12 tools available
          </span>
        </div>
      </div>
    </div>
  );
}
