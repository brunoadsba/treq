"use client";

import { useMemo, useState, useEffect } from "react";
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import { useTheme } from "../hooks/useTheme";
import { useHighContrast } from "../hooks/useHighContrast";
import { Loader2, X } from "lucide-react";

interface ChartData {
  type: "bar_chart" | "pie_chart" | "line_chart";
  title: string;
  subtitle?: string;
  description?: string;
  data: {
    labels: string[];
    datasets: Array<{
      label: string;
      data: number[];
      backgroundColor?: string | string[];
      borderColor?: string | string[];
      borderWidth?: number;
      type?: "line" | "bar";
      tension?: number;
    }>;
  };
  options?: {
    responsive?: boolean;
    maintainAspectRatio?: boolean;
    scales?: any;
    plugins?: any;
  };
  metadata?: {
    period?: string;
    unit?: string;
    total_alerts?: number;
    last_updated?: string;
    empty?: boolean;
    message?: string;
    alert_types?: string[];
    severity_levels?: Record<string, string>;
  };
}

interface ChartMessageProps {
  chartData: ChartData;
  isLoading?: boolean;
  error?: string;
}

// Cores padrão Treq
const COLORS = {
  treqYellow: "#FFCD00",
  treqYellowDark: "#E6B800",
  treqSuccess: "#10B981",
  treqSuccessDark: "#059669",
  treqError: "#EF4444",
  treqErrorDark: "#DC2626",
  treqWarning: "#F59E0B",
  treqWarningDark: "#D97706",
  treqInfo: "#3B82F6",
  treqInfoDark: "#2563EB",
};

export function ChartMessage({ chartData, isLoading = false, error }: ChartMessageProps) {
  const [theme] = useTheme();
  const isHighContrast = useHighContrast();
  const [isMobile, setIsMobile] = useState(false);
  const [mobileTooltipData, setMobileTooltipData] = useState<any>(null);

  // Detectar mobile
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 640); // sm breakpoint
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Verificar se há dados suficientes para renderizar
  const hasValidData = useMemo(() => {
    if (!chartData.data || !chartData.data.labels || chartData.data.labels.length === 0) {
      return false;
    }
    
    if (chartData.data.datasets.length === 0 || 
        chartData.data.datasets[0].data.length === 0) {
      return false;
    }
    
    return true;
  }, [chartData]);

  // Converter dados do formato Chart.js para formato Recharts
  const rechartsData = useMemo(() => {
    if (chartData.type === "pie_chart") {
      // Mapear nomes de níveis para descrições de situação
      const situationMap: Record<string, string> = {
        'Crítico': 'Ação imediata',
        'Alto': 'Requer atenção',
        'Médio': 'Monitorar',
        'Baixo': 'Normal'
      };
      
      return chartData.data.labels.map((label, index) => {
        const situation = situationMap[label] || label;
        return {
          name: situation, // Usar situação ao invés do nome do nível
          originalName: label, // Manter nome original para cores
          value: chartData.data.datasets[0].data[index],
          color: Array.isArray(chartData.data.datasets[0].backgroundColor)
            ? chartData.data.datasets[0].backgroundColor[index]
            : chartData.data.datasets[0].backgroundColor || COLORS.treqYellow,
        };
      });
    } else {
      const result: any[] = [];
      const labels = chartData.data.labels;
      const datasets = chartData.data.datasets;
      
      labels.forEach((label, labelIndex) => {
        const item: any = { name: label };
        
        datasets.forEach((dataset) => {
          if (dataset.data[labelIndex] !== undefined) {
            item[dataset.label] = dataset.data[labelIndex];
          }
        });
        
        result.push(item);
      });
      
      return result;
    }
  }, [chartData]);

  // Determinar cores baseadas no tema
  const textColor = theme === "dark" ? "#F9FAFB" : "#111827";
  const gridColor = theme === "dark" ? "#374151" : "#E5E7EB";
  const bgColor = theme === "dark" ? "#1F2937" : "#FFFFFF";
  const borderColor = theme === "dark" ? "#374151" : "#E5E7EB";

  // Altura adaptável por tipo e dispositivo - Otimizada para melhor aproveitamento de espaço
  const chartHeight = useMemo(() => {
    if (isMobile) {
      // Mobile: altura reduzida para gráfico de pizza, mais espaço para barras/linha
      return chartData.type === "pie_chart" ? 280 : 360;
    }
    // Desktop: altura maior para melhor visualização
    return chartData.type === "pie_chart" ? 450 : 500;
  }, [isMobile, chartData.type]);

  // Gerar descrição textual para acessibilidade
  const generateAriaDescription = () => {
    if (!hasValidData) return "Gráfico sem dados disponíveis";
    
    // Para gráfico de pizza, usar situações ao invés de níveis
    if (chartData.type === "pie_chart") {
      const situationMap: Record<string, string> = {
        'Crítico': 'Ação imediata',
        'Alto': 'Requer atenção',
        'Médio': 'Monitorar',
        'Baixo': 'Normal'
      };
      
      const valuesText = chartData.data.datasets[0].data
        .map((value, index) => {
          const originalLabel = chartData.data.labels[index];
          const situation = situationMap[originalLabel] || originalLabel;
          return `${situation}: ${value}`;
        })
        .join(', ');
      
      return `Gráfico ${chartData.title}. ${chartData.subtitle || ''} Valores: ${valuesText}`;
    }
    
    const valuesText = chartData.data.datasets[0].data
      .map((value, index) => `${chartData.data.labels[index]}: ${value}`)
      .join(', ');
    
    return `Gráfico ${chartData.title}. ${chartData.subtitle || ''} Valores: ${valuesText}`;
  };

  // Renderizar estado de loading
  if (isLoading) {
    return (
      <div className={`rounded-lg border p-4 sm:p-6 mb-4 sm:mb-6 ${
        theme === "dark" 
          ? "bg-treq-gray-800 border-treq-gray-700" 
          : "bg-white border-treq-gray-200"
      } shadow-sm flex flex-col items-center justify-center`}
      style={{ minHeight: `${chartHeight}px` }}
      >
        <Loader2 className="w-8 h-8 animate-spin text-treq-yellow mb-4" />
        <span className={`text-lg font-medium ${
          theme === "dark" ? "text-treq-gray-300" : "text-treq-gray-700"
        }`}>
          Gerando gráfico...
        </span>
        <p className={`text-sm mt-2 ${
          theme === "dark" ? "text-treq-gray-400" : "text-treq-gray-500"
        }`}>
          {chartData.title}
        </p>
      </div>
    );
  }

  // Renderizar erro
  if (error) {
    return (
      <div className={`rounded-lg border p-4 sm:p-6 mb-4 sm:mb-6 ${
        theme === "dark" 
          ? "bg-treq-gray-800 border-treq-error border-l-4" 
          : "bg-treq-error-light border-treq-error border-l-4"
      }`}>
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <div className={`h-5 w-5 rounded-full flex items-center justify-center ${
              theme === "dark" ? "bg-treq-error" : "bg-treq-error-light"
            }`}>
              <span className={`text-xs font-bold ${
                theme === "dark" ? "text-white" : "text-treq-error-dark"
              }`}>
                !
              </span>
            </div>
          </div>
          <div className="ml-3">
            <p className={`font-medium ${
              theme === "dark" ? "text-treq-gray-200" : "text-treq-error-dark"
            }`}>
              Erro ao carregar gráfico
            </p>
            <p className={`mt-1 text-sm ${
              theme === "dark" ? "text-treq-gray-300" : "text-treq-error-dark"
            }`}>
              {error}. Tentando carregar dados textuais...
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Renderizar mensagem de dados vazios
  if (!hasValidData || chartData.metadata?.empty) {
    return (
      <div className={`rounded-lg border p-4 sm:p-6 mb-4 sm:mb-6 ${
        theme === "dark" 
          ? "bg-treq-gray-800 border-treq-gray-700" 
          : "bg-white border-treq-gray-200"
      } shadow-sm`}>
        <div className="text-center py-12">
          <div className={`inline-block p-3 rounded-full mb-4 ${
            theme === "dark" 
              ? "bg-treq-gray-700 text-treq-gray-400" 
              : "bg-treq-gray-100 text-treq-gray-500"
          }`}>
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
          </div>
          <h3 className={`text-lg font-medium mb-1 ${
            theme === "dark" ? "text-treq-gray-200" : "text-treq-gray-900"
          }`}>
            {chartData.metadata?.message || 'Nenhum dado disponível'}
          </h3>
          <p className={`text-sm ${
            theme === "dark" ? "text-treq-gray-400" : "text-treq-gray-500"
          }`}>
            {chartData.subtitle || 'Não foi possível carregar os dados para este período.'}
          </p>
        </div>
      </div>
    );
  }

  // Função auxiliar para preparar dados do tooltip
  const prepareTooltipData = (entry: any, value: number, chartType: 'pie' | 'bar' | 'line' = 'pie') => {
    if (chartType === 'pie') {
      const total = rechartsData.reduce((sum: number, item: any) => sum + (item.value || 0), 0);
      const percent = total > 0 ? ((value / total) * 100).toFixed(1) : '0';
      
      const situationToLevelMap: Record<string, string> = {
        'Ação imediata': 'Crítico',
        'Requer atenção': 'Alto',
        'Monitorar': 'Médio',
        'Normal': 'Baixo'
      };
      
      const originalLevel = situationToLevelMap[entry.name] || entry.originalName;
      const severityDescription = chartData.metadata?.severity_levels?.[originalLevel] || '';
      const alertTypes = chartData.metadata?.alert_types || [];
      
      return {
        name: entry.name,
        value,
        percent,
        color: entry.color,
        description: severityDescription,
        alertTypes,
        chartType: 'pie'
      };
    } else {
      // Para gráficos de barras/linha
      const metricDescriptions: Record<string, string> = {
        'Pedidos Cancelados': 'Quantidade de pedidos que foram cancelados. Valores acima da meta indicam necessidade de investigação.',
        'Pedidos em Atraso': 'Quantidade de pedidos que estão com prazo de entrega vencido. Valores acima da meta requerem ação imediata.',
        'Tempo Médio (dias)': 'Tempo médio de entrega em dias. Valores acima da meta indicam necessidade de otimização do processo.',
        'Entregas no Prazo (%)': 'Percentual de entregas realizadas dentro do prazo estabelecido. Valores abaixo da meta indicam problemas operacionais.'
      };
      
      return {
        name: entry.name || entry.dataKey,
        value: entry.value,
        color: entry.color,
        description: metricDescriptions[entry.name || entry.dataKey] || chartData.description || '',
        chartType: 'bar'
      };
    }
  };

  // Modal para mobile com informações detalhadas
  const MobileTooltipModal = () => {
    if (!mobileTooltipData || !isMobile) return null;

    const { name, value, percent, color, description, alertTypes, chartType, entries } = mobileTooltipData;

    return (
      <div
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        onClick={() => setMobileTooltipData(null)}
        style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }}
      >
        <div
          className={`w-full max-w-sm rounded-lg shadow-xl border ${
            theme === "dark"
              ? "bg-treq-gray-800 border-treq-gray-700 text-treq-gray-50"
              : "bg-white border-treq-gray-200 text-treq-gray-900"
          }`}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-treq-gray-200 dark:border-treq-gray-700">
            <div className="flex items-center gap-3">
              {color && (
                <div
                  className="w-5 h-5 rounded-full flex-shrink-0"
                  style={{ backgroundColor: color }}
                />
              )}
              <div>
                <h3 className="font-semibold text-base">{name}</h3>
                {percent && (
                  <p className="text-sm text-treq-gray-500 dark:text-treq-gray-400">
                    {percent}%
                  </p>
                )}
              </div>
            </div>
            <button
              onClick={() => setMobileTooltipData(null)}
              className="p-1.5 rounded-lg hover:bg-treq-gray-100 dark:hover:bg-treq-gray-700 transition-colors"
              aria-label="Fechar"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-4 space-y-4 max-h-[60vh] overflow-y-auto">
            {(chartType === 'bar' || chartType === 'line') && entries && entries.length > 0 && (
              <div className="space-y-3">
                {entries.map((entry: any, idx: number) => {
                  const formattedValue = typeof entry.value === 'number' 
                    ? (name.includes('%') ? `${entry.value.toFixed(1)}%` : entry.value.toFixed(0))
                    : entry.value;
                  
                  return (
                    <div key={idx} className="flex items-center gap-2">
                      <div
                        className={`w-4 h-4 rounded flex-shrink-0 ${entry.isMeta ? 'bg-transparent border-2' : ''}`}
                        style={{ 
                          backgroundColor: entry.isMeta ? 'transparent' : entry.color,
                          borderColor: entry.isMeta ? entry.color : 'transparent'
                        }}
                      />
                      <span className="text-sm font-medium">{entry.name}:</span>
                      <span className="text-sm font-semibold">{formattedValue}</span>
                    </div>
                  );
                })}
              </div>
            )}
            
            {description && (
              <div className="pt-3 border-t border-treq-gray-200 dark:border-treq-gray-700">
                <p className="text-sm leading-relaxed">{description}</p>
              </div>
            )}
            
            {chartType === 'pie' && alertTypes && alertTypes.length > 0 && (
              <div className="pt-3 border-t border-treq-gray-200 dark:border-treq-gray-700">
                <p className="text-sm font-medium mb-2">Exemplos de alertas:</p>
                <ul className="space-y-1.5 text-sm">
                  {alertTypes.slice(0, 5).map((type: string, idx: number) => (
                    <li key={idx} className="flex items-start">
                      <span className="mr-2 text-treq-yellow font-bold">•</span>
                      <span>{type}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Tooltip customizado para gráfico de pizza com informações detalhadas
  const CustomPieTooltip = ({ active, payload }: any) => {
    // No mobile, usar modal ao invés de tooltip
    if (isMobile) return null;
    if (!active || !payload || !payload[0]) return null;

    const data = payload[0];
    const entry = data.payload || data;
    const tooltipData = prepareTooltipData(entry, data.value, 'pie');

    return (
      <div
        className={`px-2.5 py-2 rounded-md shadow-lg border z-50 ${
          theme === "dark"
            ? "bg-treq-gray-800 border-treq-gray-700 text-treq-gray-50"
            : "bg-white border-treq-gray-200 text-treq-gray-900"
        }`}
        style={{ 
          maxWidth: '320px',
          fontSize: '12px',
          position: 'relative',
          pointerEvents: 'none'
        }}
      >
        <div className="flex items-center gap-2 mb-2">
          <div
            className="w-4 h-4 rounded-full flex-shrink-0"
            style={{ backgroundColor: tooltipData.color }}
          />
          <span className="font-semibold text-sm">{tooltipData.name}</span>
          <span className="text-xs text-treq-gray-500 dark:text-treq-gray-400">
            ({tooltipData.percent}%)
          </span>
        </div>
        {tooltipData.description && (
          <p className="text-xs mb-2 leading-relaxed">
            {tooltipData.description}
          </p>
        )}
        {tooltipData.alertTypes && tooltipData.alertTypes.length > 0 && (
          <div className="mt-2 pt-2 border-t border-treq-gray-200 dark:border-treq-gray-700">
            <p className="text-xs font-medium mb-1">Exemplos de alertas:</p>
            <ul className="text-xs space-y-0.5">
              {tooltipData.alertTypes.slice(0, 3).map((type: string, idx: number) => (
                <li key={idx} className="flex items-start">
                  <span className="mr-1.5 flex-shrink-0">•</span>
                  <span>{type}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  // Legenda customizada expandida com descrições (para pie_chart)
  const CustomLegend = ({ payload }: any) => {
    if (!payload || !payload.length) return null;

    // Mapear nome da situação de volta para o nível original
    const situationToLevelMap: Record<string, string> = {
      'Ação imediata': 'Crítico',
      'Requer atenção': 'Alto',
      'Monitorar': 'Médio',
      'Normal': 'Baixo'
    };

    const handleLegendClick = (entry: any) => {
      if (!isMobile) return;
      
      const situationName = entry.value || entry.payload?.name || entry.name || '';
      const originalLevel = situationToLevelMap[situationName] || entry.payload?.originalName;
      const entryColor = entry.color || entry.payload?.color || COLORS.treqYellow;
      
      // Encontrar o entry correspondente no rechartsData
      const dataEntry = rechartsData.find((item: any) => item.name === situationName);
      if (!dataEntry) return;
      
      const tooltipData = prepareTooltipData(dataEntry, dataEntry.value, 'pie');
      setMobileTooltipData(tooltipData);
    };

    return (
      <div className={`${isMobile ? 'mt-2 px-1.5' : 'mt-3 px-2'} ${
        theme === "dark" ? "text-treq-gray-300" : "text-treq-gray-700"
      }`}>
        <div className={`grid grid-cols-1 ${isMobile ? 'gap-1.5' : 'sm:grid-cols-2 gap-3'} ${isMobile ? 'text-[10px]' : 'text-xs'}`}>
          {payload.map((entry: any, index: number) => {
            // Tentar obter o nome da situação de diferentes formas
            const situationName = entry.value || entry.payload?.name || entry.name || '';
            const originalLevel = situationToLevelMap[situationName] || entry.payload?.originalName;
            const severityDescription = chartData.metadata?.severity_levels?.[originalLevel] || '';
            const entryColor = entry.color || entry.payload?.color || COLORS.treqYellow;
            
            return (
              <div 
                key={index} 
                className={`flex items-start gap-1.5 ${isMobile ? 'cursor-pointer active:opacity-70' : ''}`}
                onClick={() => handleLegendClick(entry)}
              >
                <div
                  className={`${isMobile ? 'w-2 h-2' : 'w-3 h-3'} rounded-full mt-0.5 flex-shrink-0`}
                  style={{ backgroundColor: entryColor }}
                />
                <div className="flex-1 min-w-0">
                  <div className={`font-medium ${isMobile ? 'text-[10px]' : 'text-xs'}`}>{situationName}</div>
                  {severityDescription && (
                    <div className={`${isMobile ? 'text-[9px]' : 'text-xs'} mt-0.5 leading-relaxed ${
                      theme === "dark" ? "text-treq-gray-400" : "text-treq-gray-600"
                    }`}>
                      {severityDescription}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  // Tooltip customizado para gráficos de barras e linha
  const CustomBarLineTooltip = ({ active, payload, label }: any) => {
    // No mobile, nunca mostrar tooltip
    if (isMobile) return null;
    if (!active || !payload || !payload.length) return null;

    // Descrições das métricas
    const metricDescriptions: Record<string, string> = {
      'Pedidos Cancelados': 'Quantidade de pedidos que foram cancelados. Valores acima da meta indicam necessidade de investigação.',
      'Pedidos em Atraso': 'Quantidade de pedidos que estão com prazo de entrega vencido. Valores acima da meta requerem ação imediata.',
      'Tempo Médio (dias)': 'Tempo médio de entrega em dias. Valores acima da meta indicam necessidade de otimização do processo.',
      'Entregas no Prazo (%)': 'Percentual de entregas realizadas dentro do prazo estabelecido. Valores abaixo da meta indicam problemas operacionais.'
    };

    const description = metricDescriptions[label] || chartData.description || '';

    return (
      <div
        className={`px-2.5 py-2 rounded-md shadow-lg border z-50 ${
          theme === "dark"
            ? "bg-treq-gray-800 border-treq-gray-700 text-treq-gray-50"
            : "bg-white border-treq-gray-200 text-treq-gray-900"
        }`}
        style={{ 
          maxWidth: '320px',
          fontSize: '12px',
          position: 'relative',
          pointerEvents: 'none' // Não bloquear cliques
        }}
      >
        <div className={`font-semibold mb-2 ${isMobile ? 'text-xs' : 'text-sm'}`}>{label}</div>
        <div className={`space-y-1.5 ${isMobile ? 'space-y-1' : ''}`}>
          {payload.map((entry: any, index: number) => {
            const isMeta = entry.dataKey === 'Meta';
            const value = entry.value;
            const formattedValue = typeof value === 'number' 
              ? (label.includes('%') ? `${value.toFixed(1)}%` : value.toFixed(0))
              : value;
            
            return (
              <div key={index} className="flex items-center gap-2">
                <div
                  className={`${isMobile ? 'w-2.5 h-2.5' : 'w-3 h-3'} rounded flex-shrink-0 ${isMeta ? 'bg-transparent border-2' : ''}`}
                  style={{ 
                    backgroundColor: isMeta ? 'transparent' : entry.color,
                    borderColor: isMeta ? entry.color : 'transparent'
                  }}
                />
                <span className={`${isMobile ? 'text-[10px]' : 'text-xs'} font-medium flex-shrink-0`}>{entry.name}:</span>
                <span className={`${isMobile ? 'text-[10px]' : 'text-xs'} font-semibold ${
                  isMeta 
                    ? theme === "dark" ? "text-treq-gray-300" : "text-treq-gray-700"
                    : theme === "dark" ? "text-treq-gray-50" : "text-treq-gray-900"
                }`}>
                  {formattedValue}
                </span>
              </div>
            );
          })}
        </div>
        {description && (
          <div className={`mt-2 pt-2 border-t ${
            theme === "dark" ? "border-treq-gray-700" : "border-treq-gray-200"
          }`}>
            <p className={`${isMobile ? 'text-[10px]' : 'text-xs'} leading-relaxed ${
              theme === "dark" ? "text-treq-gray-300" : "text-treq-gray-700"
            }`}>
              {description}
            </p>
          </div>
        )}
      </div>
    );
  };

  // Legenda customizada expandida para gráficos de barras e linha
  const CustomBarLineLegend = ({ payload }: any) => {
    if (!payload || !payload.length) return null;

    const legendDescriptions: Record<string, string> = {
      'Valor Atual': 'Valor atual da métrica operacional medida no período selecionado.',
      'Meta': 'Meta estabelecida para esta métrica. Valores acima da meta (para métricas positivas) ou abaixo (para métricas negativas) indicam bom desempenho.'
    };

    const handleLegendClick = (entry: any) => {
      if (!isMobile) return;
      
      const description = legendDescriptions[entry.value] || '';
      setMobileTooltipData({
        name: entry.value,
        color: entry.color,
        description: description,
        chartType: 'bar'
      });
    };

    return (
      <div className={`${isMobile ? 'mt-2 px-1.5' : 'mt-3 px-2'} ${
        theme === "dark" ? "text-treq-gray-300" : "text-treq-gray-700"
      }`}>
        <div className={`flex flex-col ${isMobile ? 'gap-1.5' : 'gap-2.5'} ${isMobile ? 'text-[10px]' : 'text-xs'}`}>
          {payload.map((entry: any, index: number) => {
            const description = legendDescriptions[entry.value] || '';
            const isMeta = entry.value === 'Meta';
            
            return (
              <div 
                key={index} 
                className={`flex items-start gap-1.5 ${isMobile ? 'cursor-pointer active:opacity-70' : ''}`}
                onClick={() => handleLegendClick(entry)}
              >
                <div
                  className={`${isMobile ? 'w-2 h-2' : 'w-3 h-3'} rounded mt-0.5 flex-shrink-0 ${isMeta ? 'bg-transparent border-2' : ''}`}
                  style={{ 
                    backgroundColor: isMeta ? 'transparent' : entry.color,
                    borderColor: isMeta ? entry.color : 'transparent'
                  }}
                />
                <div className="flex-1 min-w-0">
                  <div className={`font-medium ${isMobile ? 'text-[10px]' : 'text-xs'}`}>{entry.value}</div>
                  {description && (
                    <div className={`${isMobile ? 'text-[9px]' : 'text-xs'} mt-0.5 leading-relaxed ${
                      theme === "dark" ? "text-treq-gray-400" : "text-treq-gray-600"
                    }`}>
                      {description}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  // Renderizar gráfico baseado no tipo
  const renderChart = () => {
    switch (chartData.type) {
      case "pie_chart":
        // Calcular outerRadius dinamicamente baseado na altura disponível
        // Fórmula: (altura_total - margens_top_bottom - espaço_legenda) / 2
        // Margens: top 40px + bottom 40px = 80px
        // Espaço legenda: ~100px mobile, ~120px desktop
        const pieOuterRadius = useMemo(() => {
          if (isMobile) {
            // Mobile: altura 280px - 80px margens - 100px legenda = 100px disponível / 2 = 50px máximo
            // Usar 45px para garantir espaço extra para labels que podem se estender
            return 45;
          }
          // Desktop: altura 450px - 80px margens - 120px legenda = 250px disponível / 2 = 125px máximo
          // Usar 110px para garantir espaço extra para labels que podem se estender
          return 110;
        }, [isMobile]);
        
        // Função para gerar label com situação dentro do segmento
        const renderPieLabel = ({ name, percent, cx, cy, midAngle, innerRadius, outerRadius }: any) => {
          const RADIAN = Math.PI / 180;
          const radius = innerRadius + (outerRadius - innerRadius) * 0.55;
          const x = cx + radius * Math.cos(-midAngle * RADIAN);
          const y = cy + radius * Math.sin(-midAngle * RADIAN);
          
          return (
            <text 
              x={x} 
              y={y} 
              fill="white" 
              textAnchor="middle" 
              dominantBaseline="middle"
              fontSize={isMobile ? 7 : 9}
              fontWeight="bold"
              style={{ 
                filter: 'drop-shadow(0 1px 2px rgba(0,0,0,0.9))',
                pointerEvents: 'none'
              }}
            >
              <tspan x={x} dy={isMobile ? -2.5 : -4} fontSize={isMobile ? 8 : 10}>
                {name}
              </tspan>
              <tspan x={x} dy={isMobile ? 8 : 11} fontSize={isMobile ? 7 : 9} fontWeight="normal">
                {(percent * 100).toFixed(0)}%
              </tspan>
            </text>
          );
        };
        
        return (
          <>
            <ResponsiveContainer width="100%" height={chartHeight} className="w-full">
              <PieChart margin={{ top: 40, right: 20, bottom: 40, left: 20 }}>
                <Pie
                  data={rechartsData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={renderPieLabel}
                  outerRadius={pieOuterRadius}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {rechartsData.map((entry: any, index: number) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.color} 
                      stroke={isHighContrast ? "#FFFFFF" : borderColor}
                      strokeWidth={isHighContrast ? 2 : 1}
                      onClick={isMobile ? () => {
                        const tooltipData = prepareTooltipData(entry, entry.value, 'pie');
                        setMobileTooltipData(tooltipData);
                      } : undefined}
                      style={isMobile ? { cursor: 'pointer' } : {}}
                    />
                  ))}
                </Pie>
                {!isMobile && <Tooltip content={<CustomPieTooltip />} />}
                <Legend content={<CustomLegend />} />
              </PieChart>
            </ResponsiveContainer>
          </>
        );

      case "bar_chart":
        const datasets = chartData.data.datasets;
        
        const handleBarChartClick = (data: any, index?: number) => {
          if (!isMobile) return;
          
          // O Recharts pode passar diferentes formatos de dados
          let metricName: string | null = null;
          
          if (data && typeof data === 'object') {
            // Tentar diferentes propriedades que o Recharts pode passar
            metricName = data.activeLabel || data.name || data.activePayload?.[0]?.payload?.name || null;
            
            // Se ainda não encontrou, tentar pelo index
            if (!metricName && typeof index === 'number' && rechartsData[index]) {
              metricName = rechartsData[index].name;
            }
          }
          
          if (!metricName) return;
          
          // Encontrar o entry correspondente no rechartsData
          const entry = rechartsData.find((item: any) => item.name === metricName);
          if (!entry) return;
          
          // Preparar dados do tooltip para cada série
          const tooltipEntries = datasets.map((dataset: any) => {
            const value = entry[dataset.label];
            return {
              name: dataset.label,
              value: value,
              color: dataset.backgroundColor || dataset.borderColor || COLORS.treqYellow,
              isMeta: dataset.label === 'Meta'
            };
          });
          
          const metricDescriptions: Record<string, string> = {
            'Pedidos Cancelados': 'Quantidade de pedidos que foram cancelados. Valores acima da meta indicam necessidade de investigação.',
            'Pedidos em Atraso': 'Quantidade de pedidos que estão com prazo de entrega vencido. Valores acima da meta requerem ação imediata.',
            'Tempo Médio (dias)': 'Tempo médio de entrega em dias. Valores acima da meta indicam necessidade de otimização do processo.',
            'Entregas no Prazo (%)': 'Percentual de entregas realizadas dentro do prazo estabelecido. Valores abaixo da meta indicam problemas operacionais.'
          };
          
          setMobileTooltipData({
            name: metricName,
            entries: tooltipEntries,
            description: metricDescriptions[metricName] || chartData.description || '',
            chartType: 'bar'
          });
        };
        
        return (
          <>
            <ResponsiveContainer width="100%" height={chartHeight} className="w-full">
              <BarChart 
                data={rechartsData} 
                margin={{ top: 10, right: 15, left: 10, bottom: isMobile ? 60 : 40 }}
                barCategoryGap="15%"
                barGap={3}
                onClick={isMobile ? handleBarChartClick : undefined}
              >
                <CartesianGrid 
                  strokeDasharray="3 3" 
                  stroke={gridColor} 
                  vertical={false}
                />
                <XAxis
                  dataKey="name"
                  tick={{ fill: textColor, fontSize: isMobile ? 9 : 11 }}
                  stroke={gridColor}
                  height={isMobile ? 60 : 50}
                  interval={0}
                  angle={isMobile ? -45 : -30}
                  textAnchor={isMobile ? "end" : "end"}
                  dy={isMobile ? 5 : 8}
                />
                <YAxis
                  tick={{ fill: textColor, fontSize: isMobile ? 9 : 11 }}
                  stroke={gridColor}
                  allowDecimals={false}
                  width={isMobile ? 35 : 45}
                />
                {!isMobile && <Tooltip content={<CustomBarLineTooltip />} />}
                <Legend content={<CustomBarLineLegend />} />
                {datasets.map((dataset, index) => {
                  if (dataset.type === "line") {
                    return (
                      <Line
                        key={dataset.label}
                        type="monotone"
                        dataKey={dataset.label}
                        stroke={dataset.borderColor || COLORS.treqSuccess}
                        strokeWidth={2}
                        dot={{ 
                          fill: dataset.borderColor || COLORS.treqSuccess, 
                          r: isMobile ? 3.5 : 5,
                          stroke: bgColor,
                          strokeWidth: 2
                        }}
                        activeDot={{ r: isMobile ? 6 : 7 }}
                      />
                    );
                  } else {
                    return (
                      <Bar
                        key={dataset.label}
                        dataKey={dataset.label}
                        fill={dataset.backgroundColor || COLORS.treqYellow}
                        stroke={dataset.borderColor || COLORS.treqYellowDark}
                        strokeWidth={dataset.borderWidth || 1}
                        barSize={isMobile ? 35 : 50}
                        radius={[4, 4, 0, 0]}
                        style={isMobile ? { cursor: 'pointer' } : {}}
                      />
                    );
                  }
                })}
              </BarChart>
            </ResponsiveContainer>
          </>
        );

      case "line_chart":
        const handleLineChartClick = (data: any, index?: number) => {
          if (!isMobile) return;
          
          // O Recharts pode passar diferentes formatos de dados
          let metricName: string | null = null;
          
          if (data && typeof data === 'object') {
            // Tentar diferentes propriedades que o Recharts pode passar
            metricName = data.activeLabel || data.name || data.activePayload?.[0]?.payload?.name || null;
            
            // Se ainda não encontrou, tentar pelo index
            if (!metricName && typeof index === 'number' && rechartsData[index]) {
              metricName = rechartsData[index].name;
            }
          }
          
          if (!metricName) return;
          
          // Encontrar o entry correspondente no rechartsData
          const entry = rechartsData.find((item: any) => item.name === metricName);
          if (!entry) return;
          
          // Preparar dados do tooltip para cada série
          const tooltipEntries = chartData.data.datasets.map((dataset: any) => {
            const value = entry[dataset.label];
            return {
              name: dataset.label,
              value: value,
              color: dataset.borderColor || dataset.backgroundColor || COLORS.treqInfo,
              isMeta: false
            };
          });
          
          const metricDescriptions: Record<string, string> = {
            'Pedidos Cancelados': 'Quantidade de pedidos que foram cancelados. Valores acima da meta indicam necessidade de investigação.',
            'Pedidos em Atraso': 'Quantidade de pedidos que estão com prazo de entrega vencido. Valores acima da meta requerem ação imediata.',
            'Tempo Médio (dias)': 'Tempo médio de entrega em dias. Valores acima da meta indicam necessidade de otimização do processo.',
            'Entregas no Prazo (%)': 'Percentual de entregas realizadas dentro do prazo estabelecido. Valores abaixo da meta indicam problemas operacionais.'
          };
          
          setMobileTooltipData({
            name: metricName,
            entries: tooltipEntries,
            description: metricDescriptions[metricName] || chartData.description || '',
            chartType: 'line'
          });
        };
        
        return (
          <>
            <ResponsiveContainer width="100%" height={chartHeight} className="w-full">
              <LineChart 
                data={rechartsData} 
                margin={{ top: 10, right: 15, left: 10, bottom: isMobile ? 60 : 40 }}
                onClick={isMobile ? handleLineChartClick : undefined}
              >
                <CartesianGrid 
                  strokeDasharray="3 3" 
                  stroke={gridColor} 
                />
                <XAxis
                  dataKey="name"
                  tick={{ fill: textColor, fontSize: isMobile ? 9 : 11 }}
                  stroke={gridColor}
                  height={isMobile ? 60 : 50}
                  interval={0}
                  angle={isMobile ? -45 : -30}
                  textAnchor={isMobile ? "end" : "end"}
                  dy={isMobile ? 5 : 8}
                />
                <YAxis
                  tick={{ fill: textColor, fontSize: isMobile ? 9 : 11 }}
                  stroke={gridColor}
                  width={isMobile ? 35 : 45}
                />
                {!isMobile && <Tooltip content={<CustomBarLineTooltip />} />}
                <Legend content={<CustomBarLineLegend />} />
                {chartData.data.datasets.map((dataset, index) => (
                  <Line
                    key={dataset.label}
                    type="monotone"
                    dataKey={dataset.label}
                    stroke={dataset.borderColor || COLORS.treqInfo}
                    strokeWidth={2}
                    dot={{ 
                      fill: dataset.borderColor || COLORS.treqInfo, 
                      r: isMobile ? 3.5 : 5,
                      stroke: bgColor,
                      strokeWidth: 2,
                      cursor: isMobile ? 'pointer' : 'default'
                    }}
                    activeDot={{ r: isMobile ? 6 : 7 }}
                    connectNulls
                    style={isMobile ? { cursor: 'pointer' } : {}}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </>
        );

      default:
        return (
          <div className={`p-8 text-center ${
            theme === "dark" ? "text-treq-gray-400" : "text-treq-gray-500"
          }`}>
            Tipo de gráfico não suportado: {chartData.type}
          </div>
        );
    }
  };

  return (
    <div 
      role="img"
      aria-label={`Gráfico: ${chartData.title}`}
      aria-describedby={`chart-description-${chartData.title.replace(/\s+/g, '-')}`}
      className={`w-full rounded-lg border ${
        theme === "dark"
          ? "bg-treq-gray-800 border-treq-gray-700"
          : "bg-white border-treq-gray-200"
      } shadow-sm overflow-hidden`}
    >
      {/* Título e Subtítulo - Padding otimizado */}
      <div className={`${isMobile ? 'px-2 py-1.5' : 'px-2 py-1.5 sm:px-3 sm:py-2 md:px-4 md:py-2.5'}`}>
        <h3
          className={`${isMobile ? 'text-xs' : 'text-sm sm:text-base md:text-lg'} font-semibold mb-0.5 ${
            theme === "dark" ? "text-treq-gray-50" : "text-treq-gray-900"
          }`}
        >
          {chartData.title}
        </h3>
        {chartData.subtitle && (
          <p
            className={`${isMobile ? 'text-[10px]' : 'text-xs sm:text-xs md:text-sm'} mb-1 ${
              theme === "dark" ? "text-treq-gray-400" : "text-treq-gray-600"
            }`}
          >
            {chartData.subtitle}
          </p>
        )}
        {chartData.description && (
          <p
            className={`${isMobile ? 'text-[10px]' : 'text-xs sm:text-xs md:text-sm'} leading-relaxed ${
              theme === "dark" ? "text-treq-gray-400" : "text-treq-gray-600"
            }`}
            style={{ opacity: 0.85 }}
          >
            {chartData.description}
          </p>
        )}
      </div>

      {/* Gráfico - Container responsivo otimizado para máximo aproveitamento de espaço */}
      <div className={`w-full ${chartData.type === "pie_chart" ? "overflow-visible" : "overflow-x-auto"} -mx-0`} style={{ minHeight: `${chartHeight}px` }}>
        <div style={{ width: '100%', minWidth: '100%', height: `${chartHeight}px`, overflow: chartData.type === "pie_chart" ? 'visible' : 'hidden' }}>
          {renderChart()}
        </div>
      </div>

      {/* Texto alternativo para screen readers */}
      <div id={`chart-description-${chartData.title.replace(/\s+/g, '-')}`} className="sr-only">
        {generateAriaDescription()}
      </div>

      {/* Modal para mobile */}
      <MobileTooltipModal />

      {/* Metadata (opcional) - Padding otimizado */}
      {chartData.metadata && (
        <div
          className={`${isMobile ? 'px-2 py-1' : 'px-2 py-1.5 sm:px-3 sm:py-2 md:px-4 md:py-2'} border-t ${isMobile ? 'text-[9px]' : 'text-xs'} ${
            theme === "dark"
              ? "border-treq-gray-700 text-treq-gray-400"
              : "border-treq-gray-200 text-treq-gray-500"
          }`}
        >
          {chartData.metadata.last_updated && (
            <p>
              Última atualização:{" "}
              {new Date(chartData.metadata.last_updated).toLocaleString("pt-BR")}
            </p>
          )}
          {chartData.metadata.total_alerts !== undefined && (
            <p className="mt-1">Total de alertas: {chartData.metadata.total_alerts}</p>
          )}
          {chartData.metadata.unit && (
            <p className="mt-1">Unidade: {chartData.metadata.unit}</p>
          )}
          {chartData.metadata.alert_types && (
            <div className="mt-2 pt-2 border-t border-opacity-30">
              <p className={`font-semibold mb-1 ${
                theme === "dark" ? "text-treq-gray-300" : "text-treq-gray-700"
              }`}>
                Tipos de alertas monitorados:
              </p>
              <ul className="list-disc list-inside space-y-0.5 ml-1">
                {chartData.metadata.alert_types.map((type: string, index: number) => (
                  <li key={index}>{type}</li>
                ))}
              </ul>
            </div>
          )}
          {chartData.metadata.severity_levels && (
            <div className="mt-2 pt-2 border-t border-opacity-30">
              <p className={`font-semibold mb-1 ${
                theme === "dark" ? "text-treq-gray-300" : "text-treq-gray-700"
              }`}>
                Níveis de severidade:
              </p>
              <ul className="space-y-0.5">
                {Object.entries(chartData.metadata.severity_levels).map(([level, description]: [string, any]) => (
                  <li key={level} className="flex items-start gap-1.5">
                    <span className={`font-medium ${
                      level === "Crítico" ? "text-red-500" :
                      level === "Alto" ? "text-orange-500" :
                      level === "Médio" ? "text-blue-500" :
                      "text-green-500"
                    }`}>
                      {level}:
                    </span>
                    <span>{description}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
