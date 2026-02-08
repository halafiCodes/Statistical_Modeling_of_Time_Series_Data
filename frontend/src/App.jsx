import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import { format, parseISO } from "date-fns";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  ReferenceLine
} from "recharts";

const API_BASE = "http://localhost:5000/api";

const formatDate = (value) => format(parseISO(value), "yyyy-MM-dd");

export default function App() {
  const [prices, setPrices] = useState([]);
  const [events, setEvents] = useState([]);
  const [changePoints, setChangePoints] = useState([]);
  const [start, setStart] = useState("2014-01-01");
  const [end, setEnd] = useState("2022-12-31");

  useEffect(() => {
    const fetchData = async () => {
      const [pricesRes, eventsRes, changeRes] = await Promise.all([
        axios.get(`${API_BASE}/prices`, { params: { start, end } }),
        axios.get(`${API_BASE}/events`),
        axios.get(`${API_BASE}/change-points`)
      ]);
      setPrices(pricesRes.data);
      setEvents(eventsRes.data);
      setChangePoints(changeRes.data.change_points || []);
    };

    fetchData().catch(() => {
      setPrices([]);
    });
  }, [start, end]);

  const filteredEvents = useMemo(() => {
    if (!events.length) return [];
    return events.filter((evt) => evt.date >= start && evt.date <= end);
  }, [events, start, end]);

  const chartData = useMemo(() => {
    return prices.map((row) => ({
      ...row,
      price: Number(row.price)
    }));
  }, [prices]);

  return (
    <div className="page">
      <header className="header">
        <div>
          <h1>Brent Oil Change Point Dashboard</h1>
          <p>Explore price dynamics, key events, and Bayesian change points.</p>
        </div>
        <div className="filters">
          <label>
            Start
            <input
              type="date"
              value={start}
              onChange={(e) => setStart(e.target.value)}
            />
          </label>
          <label>
            End
            <input
              type="date"
              value={end}
              onChange={(e) => setEnd(e.target.value)}
            />
          </label>
        </div>
      </header>

      <section className="card">
        <h2>Historical Brent Prices</h2>
        <div className="chart-wrapper">
          <ResponsiveContainer width="100%" height={360}>
            <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tickFormatter={formatDate} minTickGap={30} />
              <YAxis />
              <Tooltip labelFormatter={formatDate} />
              <Line type="monotone" dataKey="price" stroke="#2563eb" dot={false} />
              {filteredEvents.map((evt) => (
                <ReferenceLine
                  key={`${evt.date}-${evt.event}`}
                  x={evt.date}
                  stroke="#f59e0b"
                  strokeDasharray="4 4"
                />
              ))}
              {changePoints.map((cp) => (
                <ReferenceLine
                  key={`cp-${cp.date}`}
                  x={cp.date}
                  stroke="#ef4444"
                  strokeWidth={2}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="grid">
        <div className="card">
          <h2>Change Points</h2>
          <ul>
            {changePoints.map((cp) => (
              <li key={cp.date}>
                <strong>{cp.date}</strong> — mean before {cp.mean_before}, mean after {cp.mean_after}
                {cp.impact_pct != null ? ` (${cp.impact_pct}% change)` : ""}
              </li>
            ))}
          </ul>
        </div>
        <div className="card">
          <h2>Events in Range</h2>
          <ul>
            {filteredEvents.map((evt) => (
              <li key={`${evt.date}-${evt.event}`}>
                <strong>{evt.date}</strong> — {evt.event}
              </li>
            ))}
          </ul>
        </div>
      </section>
    </div>
  );
}
