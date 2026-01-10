const state = {
  feeds: [],
  filtered: [],
  selectedIds: new Set(),
  myFeedItems: {},
  filters: {
    category: "",
    tag: "",
    region: "",
    sourceType: "",
    search: "",
  },
};

const elements = {
  category: document.getElementById("category"),
  tag: document.getElementById("tag"),
  region: document.getElementById("region"),
  sourceType: document.getElementById("sourceType"),
  search: document.getElementById("search"),
  results: document.getElementById("results"),
  resultsCount: document.getElementById("resultsCount"),
  stats: document.getElementById("stats"),
  emptyState: document.getElementById("emptyState"),
  myFeedsCount: document.getElementById("myFeedsCount"),
  myFeedsList: document.getElementById("myFeedsList"),
  refreshMyFeeds: document.getElementById("refreshMyFeeds"),
  cardTemplate: document.getElementById("cardTemplate"),
};

const MAX_RESULTS = 25;
const MAX_MY_FEED_ITEMS = 3;
const STORAGE_KEY = "rssRegistrySelectedFeeds";

function setOptions(select, values, label) {
  const sorted = [...values].sort();
  select.innerHTML = `<option value="">All ${label}</option>`;
  sorted.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.appendChild(option);
  });
}

function applyFilters() {
  const { category, tag, region, sourceType, search } = state.filters;
  const searchTerm = search.trim().toLowerCase();

  state.filtered = state.feeds.filter((feed) => {
    if (category && feed.category !== category) return false;
    if (tag && !feed.tags.includes(tag)) return false;
    if (region && feed.region !== region) return false;
    if (sourceType && feed.source_type !== sourceType) return false;

    if (searchTerm) {
      const haystack = `${feed.title} ${feed.id}`.toLowerCase();
      if (!haystack.includes(searchTerm)) return false;
    }

    return true;
  });

  renderResults();
}

function renderResults() {
  elements.results.innerHTML = "";
  const count = state.filtered.length;
  elements.resultsCount.textContent = `${count} result${count === 1 ? "" : "s"}`;
  elements.emptyState.hidden = true;

  const limited = state.filtered.slice(0, MAX_RESULTS);

  limited.forEach((feed) => {
    const card = elements.cardTemplate.content.cloneNode(true);
    card.querySelector(".card-title").textContent = feed.title;
    card.querySelector(".badge").textContent = feed.category.replace(/_/g, " ");
    card.querySelector(
      ".card-meta"
    ).textContent = `${feed.region} • ${feed.language} • ${feed.source_type}`;

    const tagsContainer = card.querySelector(".card-tags");
    feed.tags.forEach((tag) => {
      const tagEl = document.createElement("span");
      tagEl.textContent = tag;
      tagsContainer.appendChild(tagEl);
    });

    const links = card.querySelector(".card-links");
    const siteLink = document.createElement("a");
    siteLink.href = feed.site_url;
    siteLink.textContent = "Website";
    siteLink.target = "_blank";

    const feedLink = document.createElement("a");
    feedLink.href = feed.feed_url;
    feedLink.textContent = "Feed";
    feedLink.target = "_blank";

    links.append(siteLink, feedLink);

    const addButton = card.querySelector(".add-feed");
    if (state.selectedIds.has(feed.id)) {
      addButton.textContent = "Added";
      addButton.disabled = true;
    } else {
      addButton.addEventListener("click", () => {
        addFeedToMyFeeds(feed.id);
      });
    }

    elements.results.appendChild(card);
  });

  if (count > MAX_RESULTS) {
    const note = document.createElement("p");
    note.className = "card-meta";
    note.textContent = `Showing ${MAX_RESULTS} of ${count} feeds. Refine filters to narrow further.`;
    elements.results.appendChild(note);
  } else if (count === 0) {
    elements.emptyState.hidden = false;
    elements.emptyState.innerHTML =
      "<strong>No feeds match your filters.</strong>Try clearing a filter or search term to widen the results.";
  }
}

function attachListeners() {
  elements.category.addEventListener("change", (event) => {
    state.filters.category = event.target.value;
    applyFilters();
  });

  elements.tag.addEventListener("change", (event) => {
    state.filters.tag = event.target.value;
    applyFilters();
  });

  elements.region.addEventListener("change", (event) => {
    state.filters.region = event.target.value;
    applyFilters();
  });

  elements.sourceType.addEventListener("change", (event) => {
    state.filters.sourceType = event.target.value;
    applyFilters();
  });

  elements.search.addEventListener("input", (event) => {
    state.filters.search = event.target.value;
    applyFilters();
  });

  elements.refreshMyFeeds.addEventListener("click", () => {
    refreshSelectedFeeds();
  });
}

function loadSelectedIds() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return new Set();
  try {
    const ids = JSON.parse(raw);
    if (Array.isArray(ids)) {
      return new Set(ids);
    }
  } catch (error) {
    return new Set();
  }
  return new Set();
}

function saveSelectedIds() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...state.selectedIds]));
}

function addFeedToMyFeeds(feedId) {
  state.selectedIds.add(feedId);
  saveSelectedIds();
  renderResults();
  renderMyFeeds();
}

function removeFeedFromMyFeeds(feedId) {
  state.selectedIds.delete(feedId);
  delete state.myFeedItems[feedId];
  saveSelectedIds();
  renderResults();
  renderMyFeeds();
}

function updateMyFeedsCount() {
  const count = state.selectedIds.size;
  elements.myFeedsCount.textContent = `${count} selected`;
}

function getFeedById(feedId) {
  return state.feeds.find((feed) => feed.id === feedId);
}

async function fetchFeedItems(feed) {
  const proxyUrl = `https://api.allorigins.win/raw?url=${encodeURIComponent(
    feed.feed_url
  )}`;
  const response = await fetch(proxyUrl);
  if (!response.ok) {
    throw new Error(`Fetch failed (${response.status})`);
  }
  const text = await response.text();
  const trimmed = text.trim();

  if (trimmed.startsWith("{")) {
    const data = JSON.parse(trimmed);
    const items = (data.items || []).slice(0, MAX_MY_FEED_ITEMS);
    return items.map((item) => ({
      title: item.title || "Untitled",
      link: item.url || item.external_url || "#",
    }));
  }

  const parser = new DOMParser();
  const doc = parser.parseFromString(text, "application/xml");
  if (doc.querySelector("parsererror")) {
    throw new Error("Unable to parse feed");
  }

  const entries = [
    ...doc.querySelectorAll("entry"),
    ...doc.querySelectorAll("item"),
  ].slice(0, MAX_MY_FEED_ITEMS);

  return entries.map((entry) => {
    const title = entry.querySelector("title")?.textContent?.trim() || "Untitled";
    const linkEl = entry.querySelector("link");
    const link =
      linkEl?.getAttribute("href") ||
      linkEl?.textContent?.trim() ||
      "#";

    return { title, link };
  });
}

async function refreshFeed(feedId) {
  const feed = getFeedById(feedId);
  if (!feed) return;

  state.myFeedItems[feedId] = {
    status: "loading",
    items: [],
    updatedAt: new Date().toISOString(),
  };
  renderMyFeeds();

  try {
    const items = await fetchFeedItems(feed);
    state.myFeedItems[feedId] = {
      status: "ok",
      items,
      updatedAt: new Date().toISOString(),
    };
  } catch (error) {
    state.myFeedItems[feedId] = {
      status: "error",
      items: [],
      updatedAt: new Date().toISOString(),
      message: error.message,
    };
  }

  renderMyFeeds();
}

function refreshSelectedFeeds() {
  state.selectedIds.forEach((feedId) => {
    refreshFeed(feedId);
  });
}

function renderMyFeeds() {
  elements.myFeedsList.innerHTML = "";
  updateMyFeedsCount();

  if (state.selectedIds.size === 0) {
    const empty = document.createElement("p");
    empty.className = "my-feed-empty";
    empty.textContent = "No feeds selected yet. Add feeds to start a live list.";
    elements.myFeedsList.appendChild(empty);
    return;
  }

  const selectedFeeds = [...state.selectedIds]
    .map((id) => getFeedById(id))
    .filter(Boolean);

  selectedFeeds.forEach((feed) => {
    const card = document.createElement("div");
    card.className = "my-feed-card";

    const title = document.createElement("h3");
    title.textContent = feed.title;

    const meta = document.createElement("p");
    meta.className = "my-feed-meta";
    meta.textContent = `${feed.category.replace(/_/g, " ")} • ${feed.region} • ${
      feed.source_type
    }`;

    const actions = document.createElement("div");
    actions.className = "my-feed-actions";

    const openSite = document.createElement("a");
    openSite.href = feed.site_url;
    openSite.textContent = "Website";
    openSite.target = "_blank";

    const openFeed = document.createElement("a");
    openFeed.href = feed.feed_url;
    openFeed.textContent = "Feed";
    openFeed.target = "_blank";

    const refreshBtn = document.createElement("button");
    refreshBtn.type = "button";
    refreshBtn.textContent = "Refresh";
    refreshBtn.addEventListener("click", () => refreshFeed(feed.id));

    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.textContent = "Remove";
    removeBtn.addEventListener("click", () => removeFeedFromMyFeeds(feed.id));

    actions.append(openSite, openFeed, refreshBtn, removeBtn);

    const itemsContainer = document.createElement("div");
    itemsContainer.className = "my-feed-items";

    const itemState = state.myFeedItems[feed.id];
    if (!itemState) {
      const note = document.createElement("p");
      note.className = "my-feed-meta";
      note.textContent = "No updates fetched yet.";
      itemsContainer.appendChild(note);
    } else if (itemState.status === "loading") {
      const note = document.createElement("p");
      note.className = "my-feed-meta";
      note.textContent = "Refreshing…";
      itemsContainer.appendChild(note);
    } else if (itemState.status === "error") {
      const note = document.createElement("p");
      note.className = "my-feed-meta";
      note.textContent = `Unable to load feed (${itemState.message}).`;
      itemsContainer.appendChild(note);
    } else if (itemState.items.length === 0) {
      const note = document.createElement("p");
      note.className = "my-feed-meta";
      note.textContent = "No recent items found.";
      itemsContainer.appendChild(note);
    } else {
      itemState.items.forEach((item) => {
        const link = document.createElement("a");
        link.href = item.link;
        link.textContent = item.title;
        link.target = "_blank";
        itemsContainer.appendChild(link);
      });
    }

    card.append(title, meta, actions, itemsContainer);
    elements.myFeedsList.appendChild(card);
  });
}

async function init() {
  try {
    const response = await fetch("../dist/feeds.json");
    if (!response.ok) {
      throw new Error(`Failed to load feeds.json (${response.status})`);
    }
    state.feeds = await response.json();
  } catch (error) {
    elements.stats.textContent = "Unable to load feeds.json";
    elements.resultsCount.textContent = "0 results";
    elements.emptyState.hidden = false;
    elements.emptyState.innerHTML =
      "<strong>Unable to load feeds.json.</strong>Run <code>python scripts/build/generate_outputs.py</code> and serve the repo root so <code>/dist/feeds.json</code> is available.";
    return;
  }

  const categories = new Set();
  const tags = new Set();
  const regions = new Set();
  const sourceTypes = new Set();

  state.feeds.forEach((feed) => {
    categories.add(feed.category);
    feed.tags.forEach((tag) => tags.add(tag));
    regions.add(feed.region);
    sourceTypes.add(feed.source_type);
  });

  setOptions(elements.category, categories, "categories");
  setOptions(elements.tag, tags, "tags");
  setOptions(elements.region, regions, "regions");
  setOptions(elements.sourceType, sourceTypes, "sources");

  elements.stats.textContent = `${state.feeds.length} feeds loaded`;
  state.filtered = [...state.feeds];
  state.selectedIds = loadSelectedIds();

  attachListeners();
  renderResults();
  renderMyFeeds();
}

init();
