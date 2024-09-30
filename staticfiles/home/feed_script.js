/**************************************************************
    1. API Calls
**************************************************************/

async function createRecommendedContent() {
    try {
        const position = document.querySelectorAll(
            '.pageWrapper .longFormContentContainer .recommendedContentContainer .smallFormContentWrapper .articleContainer'
        ).length;
        const res = await fetch(
            `../../api/articles/?feed_content=${position}`,
            getFetchSettings('GET')
        );
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            const context = await res.json();
            context.forEach((article) => addNewContentToContainer(article));
            document.querySelector('.recommendedContentContainer .loader').remove();
            isContentLoading = false;
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

async function createStockPitches() {
    try {
        const position = document.querySelectorAll(
            '.pageWrapper .tweetsContainer .smallFormContentWrapper .articleContainer'
        ).length;
        const res = await fetch(
            `../../api/articles/?stock_pitches=${position}`,
            getFetchSettings('GET')
        );
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            const context = await res.json();
            context.forEach((article) => addNewContentToContainer(article, true));
            document
                .querySelector('.pageWrapper .tweetsContainer .smallFormContentWrapper .loader')
                .remove();
            isContentLoading = false;
        }
    } catch (e) {
        showMessage('Error: Unexpected error has occurred!', 'Error');
    }
}

/**************************************************************
    2. Functions
**************************************************************/

function stockPitchesScroll() {
    if (
        Math.ceil(STOCK_PITCHES_CONTAINER.scrollTop + STOCK_PITCHES_CONTAINER.clientHeight) >=
            STOCK_PITCHES_CONTAINER.scrollHeight &&
        !isContentLoading
    ) {
        const loader = document.createElement('div');
        loader.classList.add('loader');
        document
            .querySelector('.pageWrapper .tweetsContainer .smallFormContentWrapper')
            .appendChild(loader);
        createStockPitches();
        isContentLoading = true;
    }
}

function contentScroll() {
    const activeTab = document.querySelector(
        '.pageWrapper .longFormContentContainer .activatedTab'
    )?.innerText;
    const loader = document.createElement('div');
    loader.classList.add('loader');
    if (!isContentLoading) {
        isContentLoading = true;
        const targetContainer =
            activeTab === 'Stock Pitches'
                ? document.querySelector('.pageWrapper .tweetsContainer .smallFormContentWrapper')
                : document.querySelector(
                      '.pageWrapper .longFormContentContainer .recommendedContentContainer'
                  );
        targetContainer.appendChild(loader);
        activeTab === 'Stock Pitches' ? createStockPitches() : createRecommendedContent();
    }
}

function addNewContentToContainer(article, stock_pitch = false) {
    const articleContainer = document.createElement('div');
    articleContainer.classList.add('articleContainer');
    articleContainer.id = 'cc#' + article.article_id;
    const leftContentSide = document.createElement('div');
    leftContentSide.classList.add('leftContentSide');
    const profileImageContainer = document.createElement('div');
    profileImageContainer.classList.add('profileImageContainer');
    const imgTag1 = document.createElement('img');
    imgTag1.src =
        'https://finbrowser.s3.us-east-2.amazonaws.com/static/' + article.source.favicon_path;
    const sourceProfile1 = document.createElement('a');
    sourceProfile1.classList.add('sourceProfile');
    sourceProfile1.href = '/source/' + article.source.slug;
    profileImageContainer.append(imgTag1, sourceProfile1);
    leftContentSide.appendChild(profileImageContainer);
    articleContainer.appendChild(leftContentSide);
    const rightContentSide = document.createElement('div');
    rightContentSide.classList.add('rightContentSide');
    const contentInfoContainer = document.createElement('div');
    contentInfoContainer.classList.add('contentInfoContainer');
    const sourceAndWebsiteContainer = document.createElement('div');
    sourceAndWebsiteContainer.classList.add('sourceAndWebsiteContainer');
    const sourceProfile2 = document.createElement('a');
    sourceProfile2.classList.add('sourceProfile');
    sourceProfile2.href = '/source/' + article.source.slug;
    sourceProfile2.innerText = article.source.name;
    const sourceWebsiteProfileContainer = document.createElement('div');
    sourceWebsiteProfileContainer.classList.add('sourceWebsiteProfileContainer');
    const imgTag2 = document.createElement('img');
    imgTag2.src =
        'https://finbrowser.s3.us-east-2.amazonaws.com/static/' + article.source.website.logo;
    const aTag1 = document.createElement('a');
    aTag1.href = article.source.url;
    sourceWebsiteProfileContainer.append(imgTag2, aTag1);
    sourceAndWebsiteContainer.append(sourceProfile2, sourceWebsiteProfileContainer);
    contentInfoContainer.appendChild(sourceAndWebsiteContainer);
    const ellipsis = document.createElement('i');
    ellipsis.classList.add('fas', 'fa-ellipsis-h');
    if (
        document
            .querySelector('.articleContainer .fa-ellipsis-h')
            .classList.contains('openAuthPrompt')
    ) {
        ellipsis.classList.add('openAuthPrompt', 'ap6');
        ellipsis.addEventListener('click', () => openAuthPrompt(ellipsis));
    }
    ellipsis.addEventListener('click', (e) => openContentOptionsMenu(e, ellipsis));
    const articleOptionsContainer = document.createElement('div');
    articleOptionsContainer.classList.add('articleOptionsContainer');
    const addToListButton = document.createElement('div');
    addToListButton.classList.add('addToListButton');
    const faList = document.createElement('i');
    faList.classList.add('fas', 'fa-list');
    const spanTag1 = document.createElement('span');
    spanTag1.innerText = 'Add to list';
    addToListButton.append(faList, spanTag1);
    addToListButton.addEventListener('click', (e) => openAddArticleToListMenu(e));
    const addToHighlightedButton = document.createElement('div');
    addToHighlightedButton.classList.add('addToHighlightedButton');
    const faHighlighter = document.createElement('i');
    faHighlighter.classList.add('fas', 'fa-highlighter');
    const spanTag2 = document.createElement('span');
    if (article.is_highlighted) {
        spanTag2.innerText = 'Unhighlight Article';
    } else {
        spanTag2.innerText = 'Highlight article';
    }
    addToHighlightedButton.append(faHighlighter, spanTag2);
    addToHighlightedButton.addEventListener('click', () =>
        changeHighlightedStatus(addToHighlightedButton)
    );
    articleOptionsContainer.append(addToListButton, addToHighlightedButton);
    contentInfoContainer.append(ellipsis, articleOptionsContainer);
    const contentBody = document.createElement('div');
    contentBody.classList.add('contentBody');
    contentBody.id = 'cc#' + article.article_id;
    const pTag1 = document.createElement('p');
    pTag1.innerText = article.title;
    contentBody.appendChild(pTag1);
    const timeContainer = document.createElement('div');
    timeContainer.classList.add('timeContainer');
    const pubDate = document.createElement('p');
    pubDate.innerText = article.pub_date;
    timeContainer.appendChild(pubDate);
    const tooltipContainer = document.createElement('div');
    tooltipContainer.classList.add('tooltipContainer');
    const paywallIcon = document.createElement('i');
    paywallIcon.classList.add('fa-solid', 'fa-lock');
    const paywallText = document.createElement('span');
    paywallText.classList.add('tooltiptext');
    if (article.source.paywall === 'No') {
        paywallIcon.classList.add('noPaywall');
        paywallText.innerText = 'No Paywall';
        tooltipContainer.classList.add('noPaywallTooltip');
    } else if (article.source.paywall === 'Semi') {
        paywallIcon.classList.add('semiPaywall');
        paywallText.innerText = 'Some Paywall';
        tooltipContainer.classList.add('semiPaywallTooltip');
    } else {
        paywallIcon.classList.add('yesPaywall');
        paywallText.innerText = 'Paywall';
        tooltipContainer.classList.add('yesPaywallTooltip');
    }
    tooltipContainer.appendChild(paywallIcon);
    tooltipContainer.appendChild(paywallText);
    timeContainer.appendChild(tooltipContainer);
    const contentLink = document.createElement('a');
    contentLink.classList.add('contentLink');
    contentLink.href = article.link;
    contentLink.target = '_blank';
    rightContentSide.append(contentInfoContainer, contentBody, contentLink);
    rightContentSide.appendChild(timeContainer);
    articleContainer.appendChild(rightContentSide);
    const targetContainer = stock_pitch
        ? document.querySelector('.pageWrapper .tweetsContainer .smallFormContentWrapper')
        : document.querySelector(
              '.pageWrapper .longFormContentContainer .recommendedContentContainer .smallFormContentWrapper'
          );
    targetContainer.appendChild(articleContainer);
}

function observeDOM() {
    const observer = new IntersectionObserver(
        (entries) => {
            entries[0].isIntersecting && contentScroll();
        },
        { threshold: 0, rootMargin: '0px 0px 30px 0px' }
    );
    observer.observe(document.querySelector('footer'));
}

/**************************************************************
    3. Other
**************************************************************/

let isContentLoading = false;

const STOCK_PITCHES_CONTAINER = document.querySelector(
    '.pageWrapper .tweetsContainer .smallFormContentWrapper'
);

/**************************************************************
    4. EventListener
**************************************************************/

document.addEventListener('DOMContentLoaded', observeDOM);

STOCK_PITCHES_CONTAINER.addEventListener('scroll', stockPitchesScroll);
