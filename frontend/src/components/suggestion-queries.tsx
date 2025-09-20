import { Button } from "@/components/ui/button";
import {
  CloudSun,
  Wheat,
  Banknote,
  Sprout,
  Calendar,
  Search,
} from "lucide-react";

interface SuggestionQueriesProps {
  onQueryClick: (query: string) => void;
}

export function SuggestionQueries({ onQueryClick }: SuggestionQueriesProps) {
  const popularQueries = [
    "Which crop is best for July?",
    "Weather forecast for this week",
    "How to apply for Kisan Credit Card?",
    "Cotton farming best practices",
    "Current mandi prices",
    "When to harvest mustard crop?",
  ];

  const categories = [
    {
      icon: CloudSun,
      name: "Weather",
      query: "What's the weather forecast for Jaipur?",
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
      icon: Sprout,
      name: "Plants",
      query: "Plant disease identification help",
    },
    { icon: Calendar, name: "Calendar", query: "Crop calendar for my region" },
    { icon: Search, name: "Market", query: "Current market prices" },
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
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {categories.map((category, index) => (
          <Button
            key={index}
            variant="outline"
            className="h-20 flex-col gap-2 hover:bg-green-50 hover:border-green-200 dark:hover:bg-green-950 dark:hover:border-green-800 transition-colors"
            onClick={() => onQueryClick(category.query)}
          >
            <category.icon className="h-5 w-5 text-green-600" />
            <span className="text-xs font-medium">{category.name}</span>
          </Button>
        ))}
      </div>

      {/* Popular Questions */}
      <div className="space-y-4">
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
          Popular Questions
        </h3>
        <div className="grid gap-2">
          {popularQueries.map((query, index) => (
            <Button
              key={index}
              variant="ghost"
              className="h-auto py-3 px-4 text-left justify-start hover:bg-muted/50 rounded-xl"
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
            Specialized for Indian agriculture
          </span>
        </div>
      </div>
    </div>
  );
}
