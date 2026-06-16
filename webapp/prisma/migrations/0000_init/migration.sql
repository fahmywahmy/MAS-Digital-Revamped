-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "public";

-- CreateEnum
CREATE TYPE "UserRole" AS ENUM ('OWNER', 'ADMIN', 'MEMBER');

-- CreateEnum
CREATE TYPE "BrandRole" AS ENUM ('OWNER', 'EDITOR', 'OPERATOR');

-- CreateEnum
CREATE TYPE "TrendStatus" AS ENUM ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED');

-- CreateEnum
CREATE TYPE "BuyerStage" AS ENUM ('AWARENESS', 'CONSIDERATION', 'DECISION', 'IMPLEMENTATION');

-- CreateEnum
CREATE TYPE "StrategyStatus" AS ENUM ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'REJECTED', 'FAILED');

-- CreateEnum
CREATE TYPE "CreativeStatus" AS ENUM ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'REJECTED', 'FAILED');

-- CreateEnum
CREATE TYPE "ContentType" AS ENUM ('REEL', 'STORY', 'POST', 'CAROUSEL', 'AD');

-- CreateEnum
CREATE TYPE "ContentStatus" AS ENUM ('DRAFT', 'IN_REVIEW', 'APPROVED', 'PUBLISHED', 'FAILED');

-- CreateEnum
CREATE TYPE "Platform" AS ENUM ('INSTAGRAM', 'TIKTOK', 'YOUTUBE', 'FACEBOOK', 'LINKEDIN', 'SNAPCHAT', 'WHATSAPP', 'GBP', 'X', 'THREADS', 'PINTEREST', 'REDDIT', 'TELEGRAM');

-- CreateEnum
CREATE TYPE "MediaType" AS ENUM ('IMAGE', 'VIDEO', 'AUDIO');

-- CreateEnum
CREATE TYPE "PublishStatus" AS ENUM ('SCHEDULED', 'PUBLISHING', 'PUBLISHED', 'FAILED');

-- CreateEnum
CREATE TYPE "InteractionType" AS ENUM ('COMMENT', 'DM', 'MENTION');

-- CreateEnum
CREATE TYPE "Sentiment" AS ENUM ('POSITIVE', 'NEGATIVE', 'NEUTRAL', 'QUESTION', 'SPAM', 'CRISIS');

-- CreateEnum
CREATE TYPE "InsightKind" AS ENUM ('AVOID_PATTERN', 'REFERENCE_EXAMPLE', 'WINNING_HOOK', 'ANOMALY', 'VOC_THEME', 'HITL_FEEDBACK_APPROVE', 'HITL_FEEDBACK_REJECT', 'HITL_FEEDBACK_ITERATE');

-- CreateEnum
CREATE TYPE "Confidence" AS ENUM ('HIGH', 'MEDIUM', 'LOW');

-- CreateEnum
CREATE TYPE "AgentType" AS ENUM ('ORCHESTRATOR', 'RESEARCH_STRATEGY', 'CREATIVE', 'ANALYTICS_SAFETY');

-- CreateEnum
CREATE TYPE "RunStatus" AS ENUM ('RUNNING', 'COMPLETED', 'FAILED');

-- CreateEnum
CREATE TYPE "AdPlatform" AS ENUM ('GOOGLE_ADS', 'META_ADS', 'LINKEDIN_ADS', 'SNAPCHAT_ADS', 'TIKTOK_ADS', 'PINTEREST_ADS', 'X_ADS', 'REDDIT_ADS');

-- CreateEnum
CREATE TYPE "CampaignObjective" AS ENUM ('AWARENESS', 'TRAFFIC', 'LEAD_GEN', 'CONVERSIONS', 'APP_INSTALLS', 'VIDEO_VIEWS', 'ENGAGEMENT', 'SALES', 'STORE_VISITS');

-- CreateEnum
CREATE TYPE "CampaignStatus" AS ENUM ('DRAFT', 'PENDING_REVIEW', 'ACTIVE', 'PAUSED', 'COMPLETED', 'REJECTED', 'FAILED', 'ARCHIVED');

-- CreateEnum
CREATE TYPE "BidStrategy" AS ENUM ('MANUAL_CPC', 'MANUAL_CPM', 'TARGET_CPA', 'TARGET_ROAS', 'MAXIMIZE_CONVERSIONS', 'MAXIMIZE_CONVERSION_VALUE', 'MAXIMIZE_CLICKS', 'LOWEST_COST', 'COST_CAP', 'BID_CAP');

-- CreateEnum
CREATE TYPE "AdFormat" AS ENUM ('SINGLE_IMAGE', 'SINGLE_VIDEO', 'CAROUSEL', 'COLLECTION', 'STORY', 'REEL', 'RESPONSIVE_SEARCH', 'RESPONSIVE_DISPLAY', 'PERFORMANCE_MAX', 'TEXT_AD', 'SNAP_STORY_AD', 'SNAP_COLLECTION', 'PROMOTED_PIN');

-- CreateEnum
CREATE TYPE "ConversionEventType" AS ENUM ('PAGE_VIEW', 'ADD_TO_CART', 'INITIATE_CHECKOUT', 'PURCHASE', 'LEAD', 'SUBSCRIBE', 'COMPLETE_REGISTRATION', 'CONTACT', 'SCHEDULE', 'SEARCH', 'CUSTOM');

-- CreateEnum
CREATE TYPE "AttributionModel" AS ENUM ('LAST_CLICK', 'FIRST_CLICK', 'LINEAR', 'POSITION_BASED', 'TIME_DECAY', 'DATA_DRIVEN');

-- CreateEnum
CREATE TYPE "ReviewSource" AS ENUM ('GOOGLE_BUSINESS', 'TRIPADVISOR', 'TRUSTPILOT', 'YELP', 'FACEBOOK', 'APPLE_MAPS', 'CUSTOM');

-- CreateTable
CREATE TABLE "User" (
    "id" UUID NOT NULL,
    "email" TEXT NOT NULL,
    "name" TEXT,
    "role" "UserRole" NOT NULL DEFAULT 'OWNER',
    "isSuperuser" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Brand" (
    "id" TEXT NOT NULL,
    "userId" UUID NOT NULL,
    "name" TEXT NOT NULL,
    "slug" TEXT NOT NULL,
    "vertical" TEXT NOT NULL,
    "targetRegions" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "language" TEXT NOT NULL DEFAULT 'ar',
    "primaryColor" TEXT NOT NULL DEFAULT '#0E6655',
    "font" TEXT NOT NULL DEFAULT 'Cairo',
    "brandVoice" TEXT NOT NULL DEFAULT '',
    "websiteUrl" TEXT,
    "competitorHandles" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "logoUrl" TEXT,
    "socialProfiles" JSONB,
    "whatsappPhoneNumberId" TEXT,
    "nameAr" TEXT,
    "taglineAr" TEXT,
    "watermarkAr" TEXT,
    "colorPalette" JSONB,
    "logoPath" TEXT,
    "logoWatermarkPath" TEXT,
    "voiceTone" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "voicePersona" TEXT,
    "targetPersona" TEXT,
    "voiceSignaturePhrases" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "voiceBannedPhrases" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "voiceExamples" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "imageMood" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "imageAnchors" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "imageBanList" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "colorAnchoring" TEXT,
    "verticalDict" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Brand_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "BrandIdentity" (
    "id" TEXT NOT NULL,
    "brandId" TEXT NOT NULL,
    "schemaVersion" INTEGER NOT NULL DEFAULT 1,
    "identity" JSONB NOT NULL DEFAULT '{}',
    "completenessPct" INTEGER NOT NULL DEFAULT 0,
    "draftedFromFile" BOOLEAN NOT NULL DEFAULT false,
    "draftedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "BrandIdentity_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "BrandMember" (
    "brandId" TEXT NOT NULL,
    "userId" UUID NOT NULL,
    "role" "BrandRole" NOT NULL DEFAULT 'OPERATOR',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "BrandMember_pkey" PRIMARY KEY ("brandId","userId")
);

-- CreateTable
CREATE TABLE "TrendScan" (
    "id" TEXT NOT NULL,
    "brandId" TEXT NOT NULL,
    "date" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "opportunities" JSONB NOT NULL,
    "status" "TrendStatus" NOT NULL DEFAULT 'PENDING',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "TrendScan_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "StrategyBrief" (
    "id" TEXT NOT NULL,
    "brandId" TEXT NOT NULL,
    "trendScanId" TEXT NOT NULL,
    "topic" TEXT NOT NULL,
    "angle" TEXT NOT NULL,
    "hooks" JSONB NOT NULL,
    "briefContent" TEXT NOT NULL,
    "buyerStage" "BuyerStage",
    "status" "StrategyStatus" NOT NULL DEFAULT 'PENDING',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "StrategyBrief_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "CreativeBrief" (
    "id" TEXT NOT NULL,
    "strategyBriefId" TEXT NOT NULL,
    "visualDirection" TEXT NOT NULL,
    "beatOutline" JSONB NOT NULL,
    "status" "CreativeStatus" NOT NULL DEFAULT 'PENDING',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "CreativeBrief_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ContentPiece" (
    "id" TEXT NOT NULL,
    "brandId" TEXT NOT NULL,
    "creativeBriefId" TEXT NOT NULL,
    "type" "ContentType" NOT NULL,
    "script" TEXT NOT NULL,
    "evalScore" INTEGER,
    "evalNotes" TEXT,
    "status" "ContentStatus" NOT NULL DEFAULT 'DRAFT',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ContentPiece_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ContentCopy" (
    "id" TEXT NOT NULL,
    "contentPieceId" TEXT NOT NULL,
    "platform" "Platform" NOT NULL,
    "caption" TEXT NOT NULL,
    "hashtags" TEXT,
    "annotations" TEXT,
    "alternatives" TEXT,
    "polishedCaption" TEXT,
    "sweepFindings" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ContentCopy_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "MediaAsset" (
    "id" TEXT NOT NULL,
    "contentPieceId" TEXT NOT NULL,
    "type" "MediaType" NOT NULL,
    "storageBucket" TEXT NOT NULL DEFAULT 'brand-media',
    "storagePath" TEXT,
    "url" TEXT NOT NULL,
    "thumbnailUrl" TEXT,
    "metadata" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "MediaAsset_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "PublishJob" (
    "id" TEXT NOT NULL,
    "contentPieceId" TEXT NOT NULL,
    "platform" "Platform" NOT NULL,
    "scheduledAt" TIMESTAMP(3),
    "publishedAt" TIMESTAMP(3),
    "externalId" TEXT,
    "status" "PublishStatus" NOT NULL DEFAULT 'SCHEDULED',
    "variantLabel" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "PublishJob_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Interaction" (
    "id" TEXT NOT NULL,
    "brandId" TEXT NOT NULL,
    "platform" "Platform" NOT NULL,
    "externalId" TEXT NOT NULL,
    "type" "InteractionType" NOT NULL,
    "content" TEXT NOT NULL,
    "sentiment" "Sentiment" NOT NULL,
    "authorName" TEXT NOT NULL,
    "authorId" TEXT NOT NULL,
    "repliedAt" TIMESTAMP(3),
    "replyContent" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Interaction_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ApprovedReply" (
    "id" TEXT NOT NULL,
    "brandId" TEXT NOT NULL,
    "interactionId" TEXT NOT NULL,
    "interactionContent" TEXT NOT NULL,
    "replyContent" TEXT NOT NULL,
    "metadata" JSONB,
    "engagement" INTEGER,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ApprovedReply_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "GeoAudit" (
    "id" TEXT NOT NULL,
    "brandId" TEXT NOT NULL,
    "date" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "siteUrl" TEXT NOT NULL,
    "crawlData" JSONB NOT NULL,
    "keywordGaps" JSONB NOT NULL,
    "recommendations" TEXT NOT NULL,
    "overallScore" INTEGER NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "GeoAudit_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "LLMCitation" (
    "id" TEXT NOT NULL,
    "brandId" TEXT NOT NULL,
    "probedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "engine" TEXT NOT NULL,
    "query" TEXT NOT NULL,
    "cited" BOOLEAN NOT NULL DEFAULT false,
    "citationUrl" TEXT,
    "position" INTEGER,
    "competitors" JSONB,
    "rawResponse" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "LLMCitation_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "GeoCompetitor" (
    "id" TEXT NOT NULL,
    "brandId" TEXT NOT NULL,
    "handle" TEXT NOT NULL,
    "name" TEXT,
    "category" TEXT,
    "websiteUrl" TEXT,
    "notes" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "GeoCompetitor_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "AnalyticsSnapshot" (
    "id" TEXT NOT NULL,
    "brandId" TEXT NOT NULL,
    "date" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "platform" "Platform" NOT NULL,
    "reach" INTEGER NOT NULL,
    "engagement" INTEGER NOT NULL,
    "saves" INTEGER NOT NULL,
    "shares" INTEGER NOT NULL,
    "comments" INTEGER NOT NULL,
    "followers" INTEGER NOT NULL,
    "metadata" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "AnalyticsSnapshot_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "BrandInsight" (
    "id" TEXT NOT NULL,
    "brandId" TEXT NOT NULL,
    "kind" "InsightKind" NOT NULL,
    "content" TEXT NOT NULL,
    "sourceType" TEXT NOT NULL,
    "sourceRef" TEXT,
    "weight" DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    "confidence" "Confidence",
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "BrandInsight_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "AgentRun" (
    "id" TEXT NOT NULL,
    "brandId" TEXT,
    "userId" UUID NOT NULL,
    "agentType" "AgentType" NOT NULL,
    "workflowId" TEXT NOT NULL,
    "status" "RunStatus" NOT NULL DEFAULT 'RUNNING',
    "startedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "completedAt" TIMESTAMP(3),
    "inputData" JSONB NOT NULL,
    "outputData" JSONB,
    "tokensUsed" INTEGER NOT NULL DEFAULT 0,
    "costUsd" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "errorMessage" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "AgentRun_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "CostLog" (
    "id" TEXT NOT NULL,
    "brandId" TEXT,
    "agentType" "AgentType" NOT NULL,
    "model" TEXT NOT NULL,
    "tokensIn" INTEGER NOT NULL,
    "tokensOut" INTEGER NOT NULL,
    "cacheReadTokens" INTEGER NOT NULL DEFAULT 0,
    "cacheCreationTokens" INTEGER NOT NULL DEFAULT 0,
    "costUsd" DOUBLE PRECISION NOT NULL,
    "category" TEXT NOT NULL,
    "toolName" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "CostLog_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "VectorMemory" (
    "id" TEXT NOT NULL,
    "brandId" TEXT NOT NULL,
    "sourceType" TEXT NOT NULL,
    "sourceId" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "metadata" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "VectorMemory_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Campaign" (
    "id" TEXT NOT NULL,
    "brandId" TEXT NOT NULL,
    "platform" "AdPlatform" NOT NULL,
    "externalId" TEXT,
    "name" TEXT NOT NULL,
    "objective" "CampaignObjective" NOT NULL,
    "status" "CampaignStatus" NOT NULL DEFAULT 'DRAFT',
    "dailyBudgetUsd" DOUBLE PRECISION,
    "lifetimeBudgetUsd" DOUBLE PRECISION,
    "bidStrategy" "BidStrategy" NOT NULL,
    "targetRoas" DOUBLE PRECISION,
    "targetCpaUsd" DOUBLE PRECISION,
    "startsAt" TIMESTAMP(3),
    "endsAt" TIMESTAMP(3),
    "metadata" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Campaign_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "AdSet" (
    "id" TEXT NOT NULL,
    "campaignId" TEXT NOT NULL,
    "externalId" TEXT,
    "name" TEXT NOT NULL,
    "status" "CampaignStatus" NOT NULL DEFAULT 'DRAFT',
    "targeting" JSONB NOT NULL,
    "dailyBudgetUsd" DOUBLE PRECISION,
    "bidAmountUsd" DOUBLE PRECISION,
    "schedule" JSONB,
    "optimizationGoal" TEXT,
    "metadata" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "AdSet_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "AdCreative" (
    "id" TEXT NOT NULL,
    "brandId" TEXT NOT NULL,
    "contentPieceId" TEXT,
    "platform" "AdPlatform" NOT NULL,
    "format" "AdFormat" NOT NULL,
    "headline" TEXT,
    "primaryText" TEXT,
    "description" TEXT,
    "ctaType" TEXT,
    "destinationUrl" TEXT NOT NULL,
    "mediaAssetId" TEXT,
    "variantLabel" TEXT,
    "evalScore" INTEGER,
    "metadata" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "AdCreative_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Ad" (
    "id" TEXT NOT NULL,
    "adSetId" TEXT NOT NULL,
    "adCreativeId" TEXT NOT NULL,
    "externalId" TEXT,
    "status" "CampaignStatus" NOT NULL DEFAULT 'DRAFT',
    "metadata" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Ad_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "AdSpend" (
    "id" TEXT NOT NULL,
    "campaignId" TEXT NOT NULL,
    "adId" TEXT,
    "date" TIMESTAMP(3) NOT NULL,
    "impressions" INTEGER NOT NULL DEFAULT 0,
    "clicks" INTEGER NOT NULL DEFAULT 0,
    "conversions" INTEGER NOT NULL DEFAULT 0,
    "conversionValueUsd" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "spendUsd" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "cpcUsd" DOUBLE PRECISION,
    "cpmUsd" DOUBLE PRECISION,
    "ctr" DOUBLE PRECISION,
    "cvr" DOUBLE PRECISION,
    "roas" DOUBLE PRECISION,
    "raw" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "AdSpend_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "PaidKeyword" (
    "id" TEXT NOT NULL,
    "brandId" TEXT NOT NULL,
    "keyword" TEXT NOT NULL,
    "matchType" TEXT,
    "searchVolume" INTEGER,
    "cpcLowUsd" DOUBLE PRECISION,
    "cpcHighUsd" DOUBLE PRECISION,
    "competition" TEXT,
    "difficulty" INTEGER,
    "intent" TEXT,
    "language" TEXT,
    "region" TEXT,
    "metadata" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "PaidKeyword_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "LandingPage" (
    "id" TEXT NOT NULL,
    "brandId" TEXT NOT NULL,
    "slug" TEXT NOT NULL,
    "url" TEXT NOT NULL,
    "title" TEXT,
    "hypothesis" TEXT,
    "status" TEXT NOT NULL DEFAULT 'active',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "LandingPage_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "LandingPageVariant" (
    "id" TEXT NOT NULL,
    "landingPageId" TEXT NOT NULL,
    "label" TEXT NOT NULL,
    "url" TEXT NOT NULL,
    "changeNotes" TEXT,
    "trafficWeight" DOUBLE PRECISION NOT NULL DEFAULT 0.5,
    "status" TEXT NOT NULL DEFAULT 'active',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "LandingPageVariant_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "LandingPageView" (
    "id" TEXT NOT NULL,
    "variantId" TEXT NOT NULL,
    "occurredAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "visitorId" TEXT NOT NULL,
    "source" TEXT,
    "medium" TEXT,
    "campaign" TEXT,
    "converted" BOOLEAN NOT NULL DEFAULT false,
    "conversionValueUsd" DOUBLE PRECISION,

    CONSTRAINT "LandingPageView_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Conversion" (
    "id" TEXT NOT NULL,
    "brandId" TEXT NOT NULL,
    "externalId" TEXT,
    "eventType" "ConversionEventType" NOT NULL,
    "eventName" TEXT,
    "valueUsd" DOUBLE PRECISION,
    "currency" TEXT NOT NULL DEFAULT 'USD',
    "occurredAt" TIMESTAMP(3) NOT NULL,
    "visitorId" TEXT,
    "emailHash" TEXT,
    "phoneHash" TEXT,
    "utmSource" TEXT,
    "utmMedium" TEXT,
    "utmCampaign" TEXT,
    "utmContent" TEXT,
    "utmTerm" TEXT,
    "attributionModel" "AttributionModel" NOT NULL DEFAULT 'LAST_CLICK',
    "attributedAdId" TEXT,
    "attributedCampaignId" TEXT,
    "attributedPublishJobId" TEXT,
    "metadata" JSONB,
    "rawPayload" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Conversion_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "AttributionTouch" (
    "id" TEXT NOT NULL,
    "conversionId" TEXT NOT NULL,
    "touchpointType" TEXT NOT NULL,
    "touchpointId" TEXT,
    "weight" DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    "occurredAt" TIMESTAMP(3) NOT NULL,
    "source" TEXT,
    "medium" TEXT,
    "campaign" TEXT,

    CONSTRAINT "AttributionTouch_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Review" (
    "id" TEXT NOT NULL,
    "brandId" TEXT NOT NULL,
    "source" "ReviewSource" NOT NULL,
    "externalId" TEXT NOT NULL,
    "authorName" TEXT,
    "rating" INTEGER NOT NULL,
    "text" TEXT,
    "language" TEXT,
    "occurredAt" TIMESTAMP(3) NOT NULL,
    "responded" BOOLEAN NOT NULL DEFAULT false,
    "responseText" TEXT,
    "respondedAt" TIMESTAMP(3),
    "metadata" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Review_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "GBPLocation" (
    "id" TEXT NOT NULL,
    "brandId" TEXT NOT NULL,
    "externalId" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "address" TEXT,
    "websiteUrl" TEXT,
    "phone" TEXT,
    "primaryCategory" TEXT,
    "metadata" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "GBPLocation_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "GBPPost" (
    "id" TEXT NOT NULL,
    "brandId" TEXT NOT NULL,
    "locationId" TEXT NOT NULL,
    "externalId" TEXT,
    "topicType" TEXT NOT NULL,
    "summary" TEXT NOT NULL,
    "ctaType" TEXT,
    "ctaUrl" TEXT,
    "mediaUrl" TEXT,
    "startTime" TIMESTAMP(3),
    "endTime" TIMESTAMP(3),
    "status" TEXT NOT NULL DEFAULT 'draft',
    "metadata" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "GBPPost_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");

-- CreateIndex
CREATE INDEX "User_email_idx" ON "User"("email");

-- CreateIndex
CREATE UNIQUE INDEX "Brand_slug_key" ON "Brand"("slug");

-- CreateIndex
CREATE UNIQUE INDEX "Brand_whatsappPhoneNumberId_key" ON "Brand"("whatsappPhoneNumberId");

-- CreateIndex
CREATE INDEX "Brand_userId_idx" ON "Brand"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "BrandIdentity_brandId_key" ON "BrandIdentity"("brandId");

-- CreateIndex
CREATE INDEX "BrandIdentity_brandId_idx" ON "BrandIdentity"("brandId");

-- CreateIndex
CREATE INDEX "BrandMember_userId_idx" ON "BrandMember"("userId");

-- CreateIndex
CREATE INDEX "TrendScan_brandId_idx" ON "TrendScan"("brandId");

-- CreateIndex
CREATE INDEX "TrendScan_date_idx" ON "TrendScan"("date");

-- CreateIndex
CREATE INDEX "StrategyBrief_brandId_idx" ON "StrategyBrief"("brandId");

-- CreateIndex
CREATE INDEX "StrategyBrief_trendScanId_idx" ON "StrategyBrief"("trendScanId");

-- CreateIndex
CREATE INDEX "StrategyBrief_buyerStage_idx" ON "StrategyBrief"("buyerStage");

-- CreateIndex
CREATE INDEX "CreativeBrief_strategyBriefId_idx" ON "CreativeBrief"("strategyBriefId");

-- CreateIndex
CREATE INDEX "ContentPiece_brandId_idx" ON "ContentPiece"("brandId");

-- CreateIndex
CREATE INDEX "ContentPiece_creativeBriefId_idx" ON "ContentPiece"("creativeBriefId");

-- CreateIndex
CREATE INDEX "ContentPiece_status_idx" ON "ContentPiece"("status");

-- CreateIndex
CREATE INDEX "ContentCopy_contentPieceId_idx" ON "ContentCopy"("contentPieceId");

-- CreateIndex
CREATE UNIQUE INDEX "ContentCopy_contentPieceId_platform_key" ON "ContentCopy"("contentPieceId", "platform");

-- CreateIndex
CREATE INDEX "MediaAsset_contentPieceId_idx" ON "MediaAsset"("contentPieceId");

-- CreateIndex
CREATE INDEX "PublishJob_contentPieceId_idx" ON "PublishJob"("contentPieceId");

-- CreateIndex
CREATE INDEX "PublishJob_platform_idx" ON "PublishJob"("platform");

-- CreateIndex
CREATE INDEX "PublishJob_status_idx" ON "PublishJob"("status");

-- CreateIndex
CREATE INDEX "Interaction_brandId_idx" ON "Interaction"("brandId");

-- CreateIndex
CREATE INDEX "Interaction_platform_idx" ON "Interaction"("platform");

-- CreateIndex
CREATE INDEX "Interaction_sentiment_idx" ON "Interaction"("sentiment");

-- CreateIndex
CREATE UNIQUE INDEX "Interaction_brandId_externalId_key" ON "Interaction"("brandId", "externalId");

-- CreateIndex
CREATE UNIQUE INDEX "ApprovedReply_interactionId_key" ON "ApprovedReply"("interactionId");

-- CreateIndex
CREATE INDEX "ApprovedReply_brandId_idx" ON "ApprovedReply"("brandId");

-- CreateIndex
CREATE INDEX "GeoAudit_brandId_idx" ON "GeoAudit"("brandId");

-- CreateIndex
CREATE INDEX "GeoAudit_date_idx" ON "GeoAudit"("date");

-- CreateIndex
CREATE INDEX "LLMCitation_brandId_engine_probedAt_idx" ON "LLMCitation"("brandId", "engine", "probedAt");

-- CreateIndex
CREATE INDEX "LLMCitation_probedAt_idx" ON "LLMCitation"("probedAt");

-- CreateIndex
CREATE INDEX "GeoCompetitor_brandId_idx" ON "GeoCompetitor"("brandId");

-- CreateIndex
CREATE UNIQUE INDEX "GeoCompetitor_brandId_handle_key" ON "GeoCompetitor"("brandId", "handle");

-- CreateIndex
CREATE INDEX "AnalyticsSnapshot_brandId_idx" ON "AnalyticsSnapshot"("brandId");

-- CreateIndex
CREATE INDEX "AnalyticsSnapshot_platform_idx" ON "AnalyticsSnapshot"("platform");

-- CreateIndex
CREATE INDEX "AnalyticsSnapshot_date_idx" ON "AnalyticsSnapshot"("date");

-- CreateIndex
CREATE INDEX "BrandInsight_brandId_kind_idx" ON "BrandInsight"("brandId", "kind");

-- CreateIndex
CREATE INDEX "BrandInsight_confidence_idx" ON "BrandInsight"("confidence");

-- CreateIndex
CREATE INDEX "AgentRun_brandId_idx" ON "AgentRun"("brandId");

-- CreateIndex
CREATE INDEX "AgentRun_userId_idx" ON "AgentRun"("userId");

-- CreateIndex
CREATE INDEX "AgentRun_agentType_idx" ON "AgentRun"("agentType");

-- CreateIndex
CREATE INDEX "AgentRun_status_idx" ON "AgentRun"("status");

-- CreateIndex
CREATE INDEX "CostLog_brandId_idx" ON "CostLog"("brandId");

-- CreateIndex
CREATE INDEX "CostLog_agentType_idx" ON "CostLog"("agentType");

-- CreateIndex
CREATE INDEX "CostLog_createdAt_idx" ON "CostLog"("createdAt");

-- CreateIndex
CREATE INDEX "VectorMemory_brandId_sourceType_idx" ON "VectorMemory"("brandId", "sourceType");

-- CreateIndex
CREATE INDEX "VectorMemory_sourceId_idx" ON "VectorMemory"("sourceId");

-- CreateIndex
CREATE UNIQUE INDEX "Campaign_externalId_key" ON "Campaign"("externalId");

-- CreateIndex
CREATE INDEX "Campaign_brandId_platform_idx" ON "Campaign"("brandId", "platform");

-- CreateIndex
CREATE INDEX "Campaign_status_idx" ON "Campaign"("status");

-- CreateIndex
CREATE INDEX "AdSet_campaignId_idx" ON "AdSet"("campaignId");

-- CreateIndex
CREATE INDEX "AdCreative_brandId_platform_idx" ON "AdCreative"("brandId", "platform");

-- CreateIndex
CREATE INDEX "Ad_adSetId_idx" ON "Ad"("adSetId");

-- CreateIndex
CREATE INDEX "AdSpend_campaignId_date_idx" ON "AdSpend"("campaignId", "date");

-- CreateIndex
CREATE INDEX "AdSpend_adId_date_idx" ON "AdSpend"("adId", "date");

-- CreateIndex
CREATE UNIQUE INDEX "AdSpend_campaignId_adId_date_key" ON "AdSpend"("campaignId", "adId", "date");

-- CreateIndex
CREATE INDEX "PaidKeyword_brandId_idx" ON "PaidKeyword"("brandId");

-- CreateIndex
CREATE UNIQUE INDEX "PaidKeyword_brandId_keyword_matchType_region_key" ON "PaidKeyword"("brandId", "keyword", "matchType", "region");

-- CreateIndex
CREATE INDEX "LandingPage_brandId_idx" ON "LandingPage"("brandId");

-- CreateIndex
CREATE UNIQUE INDEX "LandingPage_brandId_slug_key" ON "LandingPage"("brandId", "slug");

-- CreateIndex
CREATE INDEX "LandingPageVariant_landingPageId_idx" ON "LandingPageVariant"("landingPageId");

-- CreateIndex
CREATE INDEX "LandingPageView_variantId_occurredAt_idx" ON "LandingPageView"("variantId", "occurredAt");

-- CreateIndex
CREATE INDEX "Conversion_brandId_eventType_occurredAt_idx" ON "Conversion"("brandId", "eventType", "occurredAt");

-- CreateIndex
CREATE INDEX "Conversion_attributedCampaignId_idx" ON "Conversion"("attributedCampaignId");

-- CreateIndex
CREATE INDEX "Conversion_attributedAdId_idx" ON "Conversion"("attributedAdId");

-- CreateIndex
CREATE UNIQUE INDEX "Conversion_brandId_externalId_key" ON "Conversion"("brandId", "externalId");

-- CreateIndex
CREATE INDEX "AttributionTouch_conversionId_idx" ON "AttributionTouch"("conversionId");

-- CreateIndex
CREATE INDEX "AttributionTouch_touchpointType_touchpointId_idx" ON "AttributionTouch"("touchpointType", "touchpointId");

-- CreateIndex
CREATE INDEX "Review_brandId_source_idx" ON "Review"("brandId", "source");

-- CreateIndex
CREATE INDEX "Review_rating_idx" ON "Review"("rating");

-- CreateIndex
CREATE UNIQUE INDEX "Review_brandId_source_externalId_key" ON "Review"("brandId", "source", "externalId");

-- CreateIndex
CREATE INDEX "GBPLocation_brandId_idx" ON "GBPLocation"("brandId");

-- CreateIndex
CREATE UNIQUE INDEX "GBPLocation_brandId_externalId_key" ON "GBPLocation"("brandId", "externalId");

-- CreateIndex
CREATE UNIQUE INDEX "GBPPost_externalId_key" ON "GBPPost"("externalId");

-- CreateIndex
CREATE INDEX "GBPPost_brandId_idx" ON "GBPPost"("brandId");

-- CreateIndex
CREATE INDEX "GBPPost_locationId_idx" ON "GBPPost"("locationId");

-- AddForeignKey
ALTER TABLE "Brand" ADD CONSTRAINT "Brand_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "BrandIdentity" ADD CONSTRAINT "BrandIdentity_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "BrandMember" ADD CONSTRAINT "BrandMember_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "BrandMember" ADD CONSTRAINT "BrandMember_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "TrendScan" ADD CONSTRAINT "TrendScan_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "StrategyBrief" ADD CONSTRAINT "StrategyBrief_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "StrategyBrief" ADD CONSTRAINT "StrategyBrief_trendScanId_fkey" FOREIGN KEY ("trendScanId") REFERENCES "TrendScan"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CreativeBrief" ADD CONSTRAINT "CreativeBrief_strategyBriefId_fkey" FOREIGN KEY ("strategyBriefId") REFERENCES "StrategyBrief"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ContentPiece" ADD CONSTRAINT "ContentPiece_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ContentPiece" ADD CONSTRAINT "ContentPiece_creativeBriefId_fkey" FOREIGN KEY ("creativeBriefId") REFERENCES "CreativeBrief"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ContentCopy" ADD CONSTRAINT "ContentCopy_contentPieceId_fkey" FOREIGN KEY ("contentPieceId") REFERENCES "ContentPiece"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "MediaAsset" ADD CONSTRAINT "MediaAsset_contentPieceId_fkey" FOREIGN KEY ("contentPieceId") REFERENCES "ContentPiece"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "PublishJob" ADD CONSTRAINT "PublishJob_contentPieceId_fkey" FOREIGN KEY ("contentPieceId") REFERENCES "ContentPiece"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Interaction" ADD CONSTRAINT "Interaction_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ApprovedReply" ADD CONSTRAINT "ApprovedReply_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ApprovedReply" ADD CONSTRAINT "ApprovedReply_interactionId_fkey" FOREIGN KEY ("interactionId") REFERENCES "Interaction"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "GeoAudit" ADD CONSTRAINT "GeoAudit_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "LLMCitation" ADD CONSTRAINT "LLMCitation_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "GeoCompetitor" ADD CONSTRAINT "GeoCompetitor_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AnalyticsSnapshot" ADD CONSTRAINT "AnalyticsSnapshot_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "BrandInsight" ADD CONSTRAINT "BrandInsight_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AgentRun" ADD CONSTRAINT "AgentRun_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AgentRun" ADD CONSTRAINT "AgentRun_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CostLog" ADD CONSTRAINT "CostLog_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "VectorMemory" ADD CONSTRAINT "VectorMemory_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Campaign" ADD CONSTRAINT "Campaign_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AdSet" ADD CONSTRAINT "AdSet_campaignId_fkey" FOREIGN KEY ("campaignId") REFERENCES "Campaign"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AdCreative" ADD CONSTRAINT "AdCreative_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AdCreative" ADD CONSTRAINT "AdCreative_contentPieceId_fkey" FOREIGN KEY ("contentPieceId") REFERENCES "ContentPiece"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AdCreative" ADD CONSTRAINT "AdCreative_mediaAssetId_fkey" FOREIGN KEY ("mediaAssetId") REFERENCES "MediaAsset"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Ad" ADD CONSTRAINT "Ad_adSetId_fkey" FOREIGN KEY ("adSetId") REFERENCES "AdSet"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Ad" ADD CONSTRAINT "Ad_adCreativeId_fkey" FOREIGN KEY ("adCreativeId") REFERENCES "AdCreative"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AdSpend" ADD CONSTRAINT "AdSpend_campaignId_fkey" FOREIGN KEY ("campaignId") REFERENCES "Campaign"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AdSpend" ADD CONSTRAINT "AdSpend_adId_fkey" FOREIGN KEY ("adId") REFERENCES "Ad"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "PaidKeyword" ADD CONSTRAINT "PaidKeyword_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "LandingPage" ADD CONSTRAINT "LandingPage_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "LandingPageVariant" ADD CONSTRAINT "LandingPageVariant_landingPageId_fkey" FOREIGN KEY ("landingPageId") REFERENCES "LandingPage"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "LandingPageView" ADD CONSTRAINT "LandingPageView_variantId_fkey" FOREIGN KEY ("variantId") REFERENCES "LandingPageVariant"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Conversion" ADD CONSTRAINT "Conversion_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Conversion" ADD CONSTRAINT "Conversion_attributedCampaignId_fkey" FOREIGN KEY ("attributedCampaignId") REFERENCES "Campaign"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Conversion" ADD CONSTRAINT "Conversion_attributedAdId_fkey" FOREIGN KEY ("attributedAdId") REFERENCES "Ad"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Conversion" ADD CONSTRAINT "Conversion_attributedPublishJobId_fkey" FOREIGN KEY ("attributedPublishJobId") REFERENCES "PublishJob"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "AttributionTouch" ADD CONSTRAINT "AttributionTouch_conversionId_fkey" FOREIGN KEY ("conversionId") REFERENCES "Conversion"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Review" ADD CONSTRAINT "Review_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "GBPLocation" ADD CONSTRAINT "GBPLocation_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "GBPPost" ADD CONSTRAINT "GBPPost_brandId_fkey" FOREIGN KEY ("brandId") REFERENCES "Brand"("id") ON DELETE CASCADE ON UPDATE CASCADE;

