import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [table, setTable] = useState('players');
  const [data, setData] = useState([]);

  useEffect(() => {
    axios.get(`http://localhost:3001/api/${table}`)
      .then(res => setData(res.data))
      .catch(err => console.error(err));
  }, [table]);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">TFT Data Viewer</h1>
      <select
        value={table}
        onChange={e => setTable(e.target.value)}
        className="border p-2 mb-4"
      >
        <option value="players">Players</option>
        <option value="match">Match</option>
        <option value="board_details">Board Details</option>
      </select>

      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-300">
          <thead>
            <tr>
              {data[0] && Object.keys(data[0]).map((col) => (
                <th key={col} className="px-2 py-1 border">{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr key={idx}>
                {Object.values(row).map((val, i) => (
                  <td key={i} className="px-2 py-1 border">{val?.toString()}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;