import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
    TrendingUp,
    History,
    Wallet,
    BarChart3,
    Activity,
    ArrowUpRight,
    ArrowDownRight,
    Shield,
    Zap
} from 'lucide-react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    AreaChart,
    Area
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = 'http://localhost:8000';

const App = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get(`${API_BASE}/status`);
                setData(response.data);
                setLoading(false);
            } catch (error) {
                console.error("Error fetching data:", error);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 2000);
        return () => clearInterval(interval);
    }, []);

    if (loading || !data) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-background text-foreground">
                <div className="flex flex-col items-center gap-4">
                    <Zap className="w-12 h-12 text-primary animate-pulse" />
                    <h1 className="text-2xl font-bold tracking-tighter">Initializing Arbitra...</h1>
                </div>
            </div>
        );
    }

    const { capital, total_value, portfolio, trade_history, capital_history, market_prices } = data;

    return (
        <div className="min-h-screen bg-background text-foreground font-inter">
            {/* Header */}
            <header className="border-b border-border bg-background/50 backdrop-blur-md sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
                            <Shield className="w-5 h-5 text-white" />
                        </div>
                        <span className="text-xl font-bold tracking-tight">Arbitra</span>
                        <span className="px-2 py-0.5 rounded-full bg-primary/10 text-primary text-[10px] font-bold uppercase tracking-widest ml-2">
                            Autonomous
                        </span>
                    </div>
                    <div className="flex items-center gap-6">
                        <div className="flex flex-col items-end">
                            <span className="text-xs text-muted-foreground uppercase font-semibold tracking-wider">Total Value</span>
                            <span className="text-lg font-bold">${total_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                        </div>
                        <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center border border-border">
                            <Activity className="w-5 h-5 text-primary" />
                        </div>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-6 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

                    {/* Left Column: Chart & Stats */}
                    <div className="lg:col-span-8 flex flex-col gap-8">
                        <section className="bg-secondary/30 border border-border rounded-3xl p-6 lg:p-8 overflow-hidden relative">
                            <div className="flex items-center justify-between mb-8">
                                <div>
                                    <h2 className="text-2xl font-bold mb-1">Capital Evolution</h2>
                                    <p className="text-muted-foreground text-sm">Portfolio value over time</p>
                                </div>
                                <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-background border border-border">
                                    <TrendingUp className="w-4 h-4 text-primary" />
                                    <span className="text-sm font-semibold">Live Simulation</span>
                                </div>
                            </div>

                            <div className="h-[350px] w-full mt-4">
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={capital_history}>
                                        <defs>
                                            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
                                                <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                                        <XAxis
                                            dataKey="time"
                                            hide
                                        />
                                        <YAxis
                                            hide
                                            domain={['auto', 'auto']}
                                        />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: 'hsl(var(--background))', border: '1px solid hsl(var(--border))', borderRadius: '12px' }}
                                            itemStyle={{ color: 'hsl(var(--primary))', fontWeight: 'bold' }}
                                            labelStyle={{ display: 'none' }}
                                            formatter={(value) => [`$${value.toFixed(2)}`, 'Value']}
                                        />
                                        <Area
                                            type="monotone"
                                            dataKey="value"
                                            stroke="hsl(var(--primary))"
                                            strokeWidth={3}
                                            fillOpacity={1}
                                            fill="url(#colorValue)"
                                            animationDuration={1000}
                                        />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        </section>

                        <section>
                            <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                                <History className="w-5 h-5 text-primary" />
                                Recent Trades
                            </h2>
                            <div className="bg-secondary/30 border border-border rounded-3xl overflow-hidden">
                                <table className="w-full text-left">
                                    <thead>
                                        <tr className="border-b border-border bg-background/20">
                                            <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Asset</th>
                                            <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Action</th>
                                            <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Quantity</th>
                                            <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Price</th>
                                            <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Total</th>
                                            <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Rationale</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <AnimatePresence initial={false}>
                                            {trade_history.slice().reverse().map((trade) => (
                                                <motion.tr
                                                    key={trade.id}
                                                    initial={{ opacity: 0, y: -10 }}
                                                    animate={{ opacity: 1, y: 0 }}
                                                    className="border-b border-border/50 last:border-0 hover:bg-primary/5 transition-colors"
                                                >
                                                    <td className="px-6 py-4 font-bold">{trade.symbol}</td>
                                                    <td className="px-6 py-4">
                                                        <span className={`px-2.5 py-1 rounded-lg text-[10px] font-black uppercase ${trade.type === 'BUY' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'
                                                            }`}>
                                                            {trade.type}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 font-mono text-sm">{trade.quantity.toFixed(4)}</td>
                                                    <td className="px-6 py-4 font-mono text-sm">${trade.price.toLocaleString()}</td>
                                                    <td className="px-6 py-4 font-bold">${trade.total.toLocaleString(undefined, { maximumFractionDigits: 2 })}</td>
                                                    <td className="px-6 py-4 text-xs text-muted-foreground leading-relaxed max-w-xs">{trade.reason}</td>
                                                </motion.tr>
                                            ))}
                                        </AnimatePresence>
                                    </tbody>
                                </table>
                            </div>
                        </section>
                    </div>

                    {/* Right Column: Market Watch & Portfolio */}
                    <div className="lg:col-span-4 flex flex-col gap-8">
                        <section>
                            <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                                <BarChart3 className="w-5 h-5 text-primary" />
                                Market Watch
                            </h2>
                            <div className="flex flex-col gap-3">
                                {Object.entries(market_prices).map(([symbol, price]) => (
                                    <div key={symbol} className="bg-secondary/30 border border-border rounded-2xl p-5 flex items-center justify-between hover:border-primary/50 transition-all cursor-default">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 rounded-xl bg-background border border-border flex items-center justify-center font-black text-xs">
                                                {symbol.slice(0, 2)}
                                            </div>
                                            <div>
                                                <div className="font-bold">{symbol}</div>
                                                <div className="text-[10px] text-muted-foreground font-bold uppercase tracking-wider">Real-time</div>
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <div className="font-mono font-bold">${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </section>

                        <section className="bg-primary/5 border border-primary/20 rounded-3xl p-6 lg:p-8">
                            <h2 className="text-xl font-bold mb-6 flex items-center gap-2 text-primary">
                                <Wallet className="w-5 h-5" />
                                Current Portfolio
                            </h2>
                            <div className="space-y-6">
                                <div>
                                    <div className="text-xs text-muted-foreground uppercase font-bold tracking-widest mb-1">Available Cash</div>
                                    <div className="text-3xl font-black">${capital.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                                </div>
                                <div className="pt-6 border-t border-primary/10">
                                    <div className="text-xs text-muted-foreground uppercase font-bold tracking-widest mb-3">Holdings</div>
                                    <div className="grid grid-cols-2 gap-4">
                                        {Object.entries(portfolio).map(([symbol, quantity]) => (
                                            <div key={symbol} className="bg-background/50 border border-border p-3 rounded-xl">
                                                <div className="text-[10px] font-bold text-muted-foreground mb-1 uppercase tracking-tighter">{symbol}</div>
                                                <div className="font-bold truncate">{quantity.toFixed(4)}</div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </section>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default App;
