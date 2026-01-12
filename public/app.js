const state = {
  feeds: [],
  categories: [],
  tags: [],
  regions: [],
  sourceTypes: [],
  selected: new Set(),
  items: [],
  activeTags: new Set(),
};

const elements = {
  search: document.getElementById("search"),
  category: document.getElementById("category"),
  region: document.getElementById("region"),
  sourceType: document.getElementById("sourceType"),
  tagBank: document.getElementById("tagBank"),
  feedGrid: document.getElementById("feedGrid"),
  resultCount: document.getElementById("resultCount"),
  selectedList: document.getElementById("selectedList"),
  selectedCount: document.getElementById("selectedCount"),
  updatesList: document.getElementById("updatesList"),
  clearFilters: document.getElementById("clearFilters"),
  statCount: document.getElementById("stat-count"),
  statTags: document.getElementById("stat-tags"),
  refreshUpdates: document.getElementById("refreshUpdates"),
};

const STORAGE_KEY = "rss-registry-selected";

function loadSelected() {
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) return;
  try {
    JSON.parse(raw).forEach((id) => state.selected.add(id));
  } catch (err) {
    console.warn("Failed to load selections", err);
  }
}

function saveSelected() {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify([...state.selected]));
}

function setOptions(select, options, placeholder) {
  select.innerHTML = "";
  const blank = document.createElement("option");
  blank.value = "";
  blank.textContent = placeholder;
  select.appendChild(blank);
  options.forEach((option) => {
    const element = document.createElement("option");
    element.value = option.value;
    element.textContent = option.label;
    select.appendChild(element);
  });
}

function renderTagBank() {
  elements.tagBank.innerHTML = "";
  state.tags.forEach((tag) => {
    const button = document.createElement("button");
    button.className = "tag";
    button.textContent = tag.title;
    button.dataset.tag = tag.id;
    if (state.activeTags.has(tag.id)) {
      button.classList.add("active");
    }
    button.addEventListener("click", () => {
      if (state.activeTags.has(tag.id)) {
        state.activeTags.delete(tag.id);
      } else {
        state.activeTags.add(tag.id);
      }
      renderTagBank();
      renderFeeds();
    });
    elements.tagBank.appendChild(button);
  });
}

function matchesFilter(feed) {
  const query = elements.search.value.trim().toLowerCase();
  const category = elements.category.value;
  const region = elements.region.value;
  const sourceType = elements.sourceType.value;

  if (category && feed.category !== category) return false;
  if (region && feed.region !== region) return false;
  if (sourceType && feed.source_type !== sourceType) return false;

  if (state.activeTags.size) {
    const hasAll = [...state.activeTags].every((tag) => (feed.tags || []).includes(tag));
    if (!hasAll) return false;
  }

  if (query) {
    const haystack = [
      feed.title,
      feed.category,
      ...(feed.tags || []),
      feed.region,
      feed.source_type,
    ]
      .join(" ")
      .toLowerCase();
    return haystack.includes(query);
  }

  return true;
}

function renderFeeds() {
  const filtered = state.feeds.filter(matchesFilter);
  elements.feedGrid.innerHTML = "";

  filtered.forEach((feed) => {
    const card = document.createElement("article");
    card.className = "feed-card";

    const title = document.createElement("h3");
    title.textContent = feed.title;

    const meta = document.createElement("div");
    meta.className = "feed-meta";
    meta.innerHTML = `
      <span>${feed.category_title || feed.category}</span>
      <span>${feed.region_name || feed.region}</span>
      <span>${feed.source_type}</span>
    `;

    const tags = document.createElement("div");
    tags.className = "feed-meta";
    tags.textContent = (feed.tag_titles || feed.tags || []).join(" ");

    const actions = document.createElement("div");
    actions.className = "feed-actions";

    const link = document.createElement("a");
    link.href = feed.site_url;
    link.target = "_blank";
    link.rel = "noopener";
    link.textContent = "Visit site";

    const select = document.createElement("button");
    select.className = "select-btn";
    const isSelected = state.selected.has(feed.id);
    if (isSelected) {
      select.classList.add("active");
    }
    select.textContent = isSelected ? "Remove" : "Add";
    select.addEventListener("click", () => toggleSelection(feed.id));

    actions.appendChild(link);
    actions.appendChild(select);

    card.appendChild(title);
    card.appendChild(meta);
    card.appendChild(tags);
    card.appendChild(actions);

    elements.feedGrid.appendChild(card);
  });

  elements.resultCount.textContent = `${filtered.length} feeds`;
}

function toggleSelection(id) {
  if (state.selected.has(id)) {
    state.selected.delete(id);
  } else {
    state.selected.add(id);
  }
  saveSelected();
  renderFeeds();
  renderSelected();
  renderUpdates();
}

function renderSelected() {
  const list = [...state.selected]
    .map((id) => state.feeds.find((feed) => feed.id === id))
    .filter(Boolean);

  elements.selectedList.innerHTML = "";
  list.forEach((feed) => {
    const item = document.createElement("div");
    item.className = "selected-item";

    const title = document.createElement("strong");
    title.textContent = feed.title;

    const meta = document.createElement("div");
    meta.className = "feed-meta";
    meta.textContent = `${feed.category_title || feed.category} ? ${feed.region_name || feed.region}`;

    const remove = document.createElement("button");
    remove.textContent = "Remove";
    remove.addEventListener("click", () => toggleSelection(feed.id));

    item.appendChild(title);
    item.appendChild(meta);
    item.appendChild(remove);
    elements.selectedList.appendChild(item);
  });

  elements.selectedCount.textContent = `${list.length} selected`;
}

function renderUpdates() {
  elements.updatesList.innerHTML = "";
  const selectedItems = state.items.filter((item) => state.selected.has(item.feed_id));
  const display = selectedItems.slice(0, 8);

  if (!display.length) {
    const empty = document.createElement("div");
    empty.className = "update-item";
    empty.textContent = "Select feeds to preview demo updates.";
    elements.updatesList.appendChild(empty);
    return;
  }

  display.forEach((item) => {
    const block = document.createElement("div");
    block.className = "update-item";

    const title = document.createElement("h4");
    title.textContent = item.title;

    const meta = document.createElement("div");
    meta.className = "feed-meta";
    meta.textContent = `${item.feed_title} ? ${new Date(item.published).toLocaleString()}`;

    const link = document.createElement("a");
    link.href = item.url;
    link.target = "_blank";
    link.rel = "noopener";
    link.textContent = "Open";

    block.appendChild(title);
    block.appendChild(meta);
    block.appendChild(link);

    elements.updatesList.appendChild(block);
  });
}

function clearFilters() {
  elements.search.value = "";
  elements.category.value = "";
  elements.region.value = "";
  elements.sourceType.value = "";
  state.activeTags.clear();
  renderTagBank();
  renderFeeds();
}

function shuffleUpdates() {
  state.items.sort(() => Math.random() - 0.5);
  renderUpdates();
}

async function init() {
  loadSelected();

  const response = await fetch("/dist/feeds.json");
  const data = await response.json();
  const itemsResponse = await fetch("/dist/items.json");
  const items = await itemsResponse.json();

  state.feeds = data.feeds;
  state.categories = data.categories;
  state.tags = data.tags;
  state.regions = data.regions;
  state.items = items;

  state.sourceTypes = [...new Set(state.feeds.map((feed) => feed.source_type))].sort();

  setOptions(
    elements.category,
    state.categories.map((item) => ({ value: item.id, label: item.title })),
    "All categories"
  );
  setOptions(
    elements.region,
    state.regions.map((item) => ({ value: item.code, label: item.name })),
    "All regions"
  );
  setOptions(
    elements.sourceType,
    state.sourceTypes.map((value) => ({ value, label: value })),
    "All source types"
  );

  renderTagBank();
  renderFeeds();
  renderSelected();
  renderUpdates();

  elements.statCount.textContent = `${state.feeds.length} feeds`;
  elements.statTags.innerHTML = state.categories
    .slice(0, 3)
    .map((item) => `<span>${item.title}</span>`)
    .join("");
}

["input", "change"].forEach((eventName) => {
  elements.search.addEventListener(eventName, renderFeeds);
  elements.category.addEventListener(eventName, renderFeeds);
  elements.region.addEventListener(eventName, renderFeeds);
  elements.sourceType.addEventListener(eventName, renderFeeds);
});

elements.clearFilters.addEventListener("click", clearFilters);
elements.refreshUpdates.addEventListener("click", shuffleUpdates);

init().catch((error) => {
  console.error("Failed to initialize", error);
  elements.feedGrid.innerHTML = "<p>Failed to load feed data. Run the build script.</p>";
});
