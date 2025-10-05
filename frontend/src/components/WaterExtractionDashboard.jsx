import React, { useMemo } from 'react';
import { Bar, Line, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  PointElement,
  LineElement,
  ArcElement,
} from 'chart.js';

// Note: You may need to adjust the path to where your ImageViewer.js file is located.
import ImageViewer from './ImageViewer'; 

// Register Chart.js components
ChartJS.register(
  CategoryScale, LinearScale, BarElement, PointElement, LineElement, ArcElement, Title, Tooltip, Legend
);

// Helper function to create a readable label from a data key
const formatMetricKey = (key) => {
  if (!key) return '';
  return key
    .replace(/_/g, ' ') // replace underscores with spaces
    .replace('percent', '(%)') // special case for percent
    .replace('ham', '(ham)') // special case for hectometer
    .replace(/\b\w/g, l => l.toUpperCase()); // capitalize words
};

const WaterExtractionDashboard = ({ data: rawData }) => {
  
  if (!rawData || rawData.length === 0) {
    return <ImageViewer imageUrl={null} />;
  }

  // --- DYNAMICALLY FIND THE PRIMARY METRIC KEY ---
  const metricKey = useMemo(() => {
    if (!rawData || rawData.length === 0) return null;
    const knownDimensionKeys = ['state', 'district', 'year'];
    const firstItemKeys = Object.keys(rawData[0]);
    return firstItemKeys.find(key => typeof rawData[0][key] === 'number' && !knownDimensionKeys.includes(key));
  }, [rawData]);
  
  const metricLabel = useMemo(() => formatMetricKey(metricKey), [metricKey]);

  // --- ANALYZE THE SHAPE OF THE DATA ---
  const { uniqueYears, uniqueDistricts, uniqueStates } = useMemo(() => {
    const years = new Set(rawData.map(item => item.year).filter(y => y != null));
    const districts = new Set(rawData.map(item => item.district));
    const states = new Set(rawData.map(item => item.state));
    return { 
      uniqueYears: Array.from(years).sort((a, b) => a - b),
      uniqueDistricts: Array.from(districts).sort(),
      uniqueStates: Array.from(states).sort(),
    };
  }, [rawData]);

  const hasMultipleDistricts = uniqueDistricts.length > 1;
  const hasMultipleYears = uniqueYears.length > 1;
  const hasData = rawData && rawData.length > 0 && metricKey;

  // --- CHART DATA PREPARATION (code is unchanged, kept for context) ---
  const barChartData = useMemo(() => {
    if (!hasData || !hasMultipleDistricts) return null;
    let districtMetrics = rawData.map(item => ({ district: item.district, value: item[metricKey] }));
    districtMetrics.sort((a, b) => b.value - a.value);
    return {
      labels: districtMetrics.map(d => d.district),
datasets: [{
  label: metricLabel,
  data: districtMetrics.map(d => d.value),
  backgroundColor: (ctx) => {
    const chart = ctx.chart;
    const { ctx: canvasCtx, chartArea } = chart;
    if (!chartArea) return null;
    const gradient = canvasCtx.createLinearGradient(0, 0, 0, chartArea.bottom);
    gradient.addColorStop(0, 'rgba(0, 200, 255, 0.9)');
    gradient.addColorStop(1, 'rgba(0, 100, 255, 0.3)');
    return gradient;
  },
  borderColor: '#00B4FF',
  borderWidth: 2,
  borderRadius: 8,
  hoverBackgroundColor: 'rgba(0, 180, 255, 0.9)',
  hoverBorderColor: '#0090FF',
  barPercentage: 0.7,
  categoryPercentage: 0.6,
}]

    };
  }, [rawData, hasData, hasMultipleDistricts, metricKey, metricLabel]);

  const lineChartData = useMemo(() => {
    if (!hasData || !hasMultipleYears) return null;
    const yearlyTotals = rawData.reduce((acc, item) => {
      acc[item.year] = (acc[item.year] || 0) + item[metricKey];
      return acc;
    }, {});
    const sortedYears = Object.keys(yearlyTotals).sort((a,b) => a-b);
    const trendData = sortedYears.map(year => yearlyTotals[year]);
    return {
      labels: sortedYears,
      datasets: [{
        label: hasMultipleDistricts ? `Sum of ${metricLabel}` : metricLabel,
        data: trendData,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      }],
    };
  }, [rawData, hasData, hasMultipleYears, metricKey, metricLabel, hasMultipleDistricts]);

  const pieChartData = useMemo(() => {
    if (!hasData || !hasMultipleDistricts) return null;
    const districtTotals = rawData.reduce((acc, item) => {
        acc[item.district] = (acc[item.district] || 0) + item[metricKey];
        return acc;
    }, {});
    const sortedTotals = Object.entries(districtTotals).sort(([, a], [, b]) => b - a);
    const topN = 10;
    const topData = sortedTotals.slice(0, topN);
    const otherDataSum = sortedTotals.slice(topN).reduce((sum, [, value]) => sum + value, 0);
    const labels = [...topData.map(([district]) => district), ...(otherDataSum > 0 ? ['Others'] : [])];
    const data = [...topData.map(([, value]) => value), ...(otherDataSum > 0 ? [otherDataSum] : [])];
    return {
      labels,
      datasets: [{
        data,
        backgroundColor: ['#4BC0C0', '#FF6384', '#FFCE56', '#9966FF', '#36A2EB', '#FF9F40', '#2ECC71', '#E74C3C', '#3498DB', '#F1C40F', '#8E44AD', '#E67E22', '#C9CBCF'],
      }],
    };
  }, [rawData, hasData, hasMultipleDistricts, metricKey]);
  // --- END OF CHART DATA PREPARATION ---

  const chartOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top' } }};
  
  const renderCharts = () => {
    if (!hasData) return <p>Could not determine a metric to visualize from the data.</p>;

    const showBar = barChartData && hasMultipleDistricts;
    const showLine = lineChartData && hasMultipleYears;
    const showPie = pieChartData && hasMultipleDistricts;

    return (
        <main className="space-y-8">
            {showBar && (
              <div>
                <h2 className="text-lg font-semibold text-gray-700 mb-4">District Comparison {uniqueYears.length === 1 ? `for ${uniqueYears[0]}` : ''}</h2>
                <div className="relative" style={{ height: '400px' }}><Bar options={chartOptions} data={barChartData} /></div>
              </div>
            )}
            {showLine && (
              <div>
                <h2 className="text-lg font-semibold text-gray-700 mb-4">Trend Over Time</h2>
                <div className="relative" style={{ height: '350px' }}><Line options={chartOptions} data={lineChartData} /></div>
              </div>
            )}
            {showPie && (
              <div>
                 <h2 className="text-lg font-semibold text-gray-700 mb-4">District Contribution</h2>
                 <div className="relative flex justify-center" style={{ height: '350px' }}><Pie options={{...chartOptions, maintainAspectRatio: false }} data={pieChartData} /></div>
              </div>
            )}
             {!showBar && !showLine && !showPie && (
               <p className="text-gray-600">The provided data is not suitable for the available chart types (e.g., single data point).</p>
             )}
        </main>
    );
  };

  // --- STYLE CHANGE IS HERE ---
  // Changed `shadow-md` to `border` and `p-4 sm:p-6` to `p-6` for consistency.
  return (
    <div className="bg-surface rounded-lg border w-full h-full p-6 overflow-y-auto">
      <header className="mb-6">
        <h1 className="text-xl sm:text-2xl font-bold text-gray-800">
          {metricLabel} Analysis for {uniqueStates.join(', ')}
        </h1>
      </header>
      {renderCharts()}
    </div>
  );
};

export default WaterExtractionDashboard;