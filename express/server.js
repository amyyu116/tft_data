require('dotenv').config();
const express = require('express');
const { Pool } = require('pg');
const cors = require('cors');

const app = express();
app.use(cors());

const pool = new Pool({
  user: process.env.PGUSER,
  password: process.env.PGPASSWORD,
  host: process.env.PGHOST,
  database: process.env.PGDATABASE,
  port: process.env.PGPORT,
});

pool.query('SELECT NOW()', (err, res) => {
  if (err) {
    console.error('DB connection failed:', err.stack);
  } else {
    console.log('DB connected at:', res.rows[0].now);
  }
});

app.get('/api/:table', async (req, res) => {
  const table = req.params.table;
  if (!['board_details', 'match', 'players'].includes(table)) {
    return res.status(400).json({ error: 'Invalid table name' });
  }

  try {
    const result = await pool.query(`SELECT * FROM ${table} LIMIT 100`);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});