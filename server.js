const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
app.use(express.json());
app.use(cors());

app.post('/api/webhooks/weather-trigger', async (req, res) => {
    const { rainfall_mm_hr, duration_mins } = req.body;

    if (rainfall_mm_hr > 15 && duration_mins >= 45) {
        try {
            const fraudResponse = await axios.post('http://localhost:8000/api/fraud-score', {
                worker_id: "worker_123",
                zone: "zone1"
            });

            if (fraudResponse.data.fraud_score < 0.2) {
                return res.status(200).json({ status: "Claim Auto-Approved" });
            } else {
                return res.status(403).json({ status: "Flagged" });
            }
        } catch (error) {
            return res.status(500).send("ML error");
        }
    }

    res.send("No trigger");
});

app.listen(3001, () => console.log("Server running"));
