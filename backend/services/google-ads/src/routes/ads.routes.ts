import { Router } from 'express';
import { GoogleAdsService } from '../services/GoogleAdsService';
import { validateConfig } from '../middleware/validateConfig';
import logger from '../utils/logger';

const router = Router();
let adsService: GoogleAdsService;

// Middleware to initialize the service with config
router.use(validateConfig, (req, res, next) => {
  if (!adsService) {
    adsService = new GoogleAdsService(req.app.locals.googleAdsConfig);
  }
  next();
});

// Campaign routes
router.post('/campaigns', async (req, res) => {
  try {
    const campaign = await adsService.createCampaign(req.body);
    res.status(201).json(campaign);
  } catch (error) {
    logger.error('Error in campaign creation', { error });
    res.status(500).json({ error: 'Failed to create campaign' });
  }
});

// Ad Group routes
router.post('/ad-groups', async (req, res) => {
  try {
    const adGroup = await adsService.createAdGroup(req.body);
    res.status(201).json(adGroup);
  } catch (error) {
    logger.error('Error in ad group creation', { error });
    res.status(500).json({ error: 'Failed to create ad group' });
  }
});

// Ad routes
router.post('/ads', async (req, res) => {
  try {
    const ad = await adsService.createAd(req.body);
    res.status(201).json(ad);
  } catch (error) {
    logger.error('Error in ad creation', { error });
    res.status(500).json({ error: 'Failed to create ad' });
  }
});

// Performance report routes
router.get('/campaigns/:campaignId/performance', async (req, res) => {
  try {
    const { start, end } = req.query;
    const report = await adsService.getPerformanceReport(
      req.params.campaignId,
      { start: start as string, end: end as string }
    );
    res.json(report);
  } catch (error) {
    logger.error('Error fetching performance report', { error });
    res.status(500).json({ error: 'Failed to fetch performance report' });
  }
});

// Keyword metrics routes
router.get('/ad-groups/:adGroupId/keywords', async (req, res) => {
  try {
    const metrics = await adsService.getKeywordMetrics(req.params.adGroupId);
    res.json(metrics);
  } catch (error) {
    logger.error('Error fetching keyword metrics', { error });
    res.status(500).json({ error: 'Failed to fetch keyword metrics' });
  }
});

export default router; 