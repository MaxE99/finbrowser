let contentIsLoading = false;

function createTwitterPart(content, rightContentSide) {
    if (content.tweet_type.type === 'Retweet') {
        const retweetWrapper = document.createElement('div');
        retweetWrapper.className = 'retweetWrapper';
        const author = document.createElement('span');
        author.textContent = `@${content.tweet_type.author}`;
        retweetWrapper.appendChild(document.createTextNode('Retweeted post by '));
        retweetWrapper.appendChild(author);
        rightContentSide.appendChild(retweetWrapper);
    }

    if (content.tweet_type.type === 'Reply') {
        const replyWrapper = document.createElement('div');
        replyWrapper.className = 'replyWrapper';
        const author = document.createElement('span');
        author.textContent = `@${content.tweet_type.author}`;
        replyWrapper.appendChild(document.createTextNode('Replying to '));
        replyWrapper.appendChild(author);
        rightContentSide.appendChild(replyWrapper);
    }

    if (content.tweet_type.image_path) {
        const tweetImage = document.createElement('img');
        tweetImage.className = 'tweetImage';
        tweetImage.setAttribute(
            'src',
            'https://finbrowser.s3.us-east-2.amazonaws.com/static/' + content.tweet_type.image_path
        );
        tweetImage.setAttribute('alt', 'Tweet Image');
        rightContentSide.appendChild(tweetImage);
    }

    if (
        content.tweet_type.type === 'Quote' ||
        content.tweet_type.type === 'Retweet' ||
        content.tweet_type.type === 'Reply'
    ) {
        const quoteWrapper = document.createElement('div');
        quoteWrapper.className = 'quoteWrapper';

        const quoteUpperContainer = document.createElement('div');
        quoteUpperContainer.className = 'quoteUpperContainer';

        const quoteAuthor = document.createElement('div');
        quoteAuthor.className = 'quoteAuthor';
        quoteAuthor.textContent = content.tweet_type.author;

        quoteUpperContainer.appendChild(quoteAuthor);
        quoteWrapper.appendChild(quoteUpperContainer);

        const quoteText = document.createElement('div');
        quoteText.className = 'quoteText';
        quoteText.textContent = content.tweet_type.text;
        quoteWrapper.appendChild(quoteText);

        if (content.tweet_type.initial_tweet_img_path) {
            const tweetImage = document.createElement('img');
            tweetImage.className = 'tweetImage';
            tweetImage.setAttribute(
                'src',
                'https://finbrowser.s3.us-east-2.amazonaws.com/static/' +
                    content.tweet_type.initial_tweet_img_path
            );
            tweetImage.setAttribute('alt', 'Tweet Reply Image');
            quoteWrapper.appendChild(tweetImage);
        }

        rightContentSide.appendChild(quoteWrapper);

        rightContentSide.appendChild(contentLink);
    }
}

function addNewContentToContainer(article, tweet = false) {
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
        ellipsis.addEventListener('click', () => {
            openAuthPrompt(ellipsis);
        });
    }
    ellipsis.addEventListener('click', (e) => {
        openContentOptionsMenu(e, ellipsis);
    });
    const articleOptionsContainer = document.createElement('div');
    articleOptionsContainer.classList.add('articleOptionsContainer');
    const addToListButton = document.createElement('div');
    addToListButton.classList.add('addToListButton');
    const faList = document.createElement('i');
    faList.classList.add('fas', 'fa-list');
    const spanTag1 = document.createElement('span');
    spanTag1.innerText = 'Add to list';
    addToListButton.append(faList, spanTag1);
    addToListButton.addEventListener('click', (e) => {
        openAddToListMenu(e);
    });
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
    addToHighlightedButton.addEventListener('click', () => {
        highlightContent(addToHighlightedButton);
    });
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
    const pTag2 = document.createElement('p');
    pTag2.innerText = article.pub_date;
    timeContainer.appendChild(pTag2);
    contentLink = document.createElement('a');
    contentLink.classList.add('contentLink');
    contentLink.href = article.link;
    rightContentSide.append(contentInfoContainer, contentBody, contentLink);
    if (tweet) {
        createTwitterPart(article, rightContentSide);
        rightContentSide.appendChild(timeContainer);
        articleContainer.appendChild(rightContentSide);
        document
            .querySelector('.pageWrapper .tweetsContainer .smallFormContentWrapper')
            .appendChild(articleContainer);
    } else {
        rightContentSide.appendChild(timeContainer);
        articleContainer.appendChild(rightContentSide);
        document
            .querySelector(
                '.pageWrapper .longFormContentContainer .recommendedContentContainer .smallFormContentWrapper'
            )
            .appendChild(articleContainer);
    }
}

async function createContent() {
    try {
        const position = document.querySelectorAll(
            '.pageWrapper .longFormContentContainer .recommendedContentContainer .smallFormContentWrapper .articleContainer'
        ).length;
        const res = await fetch(
            `../../api/articles/?feed_content=${position}`,
            get_fetch_settings('GET')
        );
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            const context = await res.json();
            context.forEach((article) => {
                addNewContentToContainer(article);
            });
            document.querySelector('.recommendedContentContainer .loader').remove();
            contentIsLoading = false;
        }
    } catch (e) {
        // showMessage("Error: Unexpected error has occurred!", "Error");
    }
}

async function createTweets() {
    try {
        const position = document.querySelectorAll(
            '.pageWrapper .tweetsContainer .smallFormContentWrapper .articleContainer'
        ).length;
        const res = await fetch(
            `../../api/articles/?best_tweets=${position}`,
            get_fetch_settings('GET')
        );
        if (!res.ok) {
            showMessage('Error: Network request failed unexpectedly!', 'Error');
        } else {
            const context = await res.json();
            context.forEach((article) => {
                addNewContentToContainer(article, true);
            });
            document
                .querySelector('.pageWrapper .tweetsContainer .smallFormContentWrapper .loader')
                .remove();
            contentIsLoading = false;
        }
    } catch (e) {
        // showMessage("Error: Unexpected error has occurred!", "Error");
    }
}

window.addEventListener('scroll', () => {
    const { scrollHeight, scrollTop, clientHeight } = document.documentElement;
    if (scrollTop + clientHeight > scrollHeight - 5 && !contentIsLoading) {
        const loader = document.createElement('div');
        loader.classList.add('loader');
        if (
            window.innerWidth < 1001 &&
            document
                .querySelector('.pageWrapper .tweetsContainer')
                .classList.contains('tabsContentActive')
        ) {
            document
                .querySelector('.pageWrapper .tweetsContainer .smallFormContentWrapper')
                .appendChild(loader);
            createTweets();
            contentIsLoading = true;
        } else {
            document
                .querySelector(
                    '.pageWrapper .longFormContentContainer .recommendedContentContainer'
                )
                .appendChild(loader);
            createContent();
            contentIsLoading = true;
        }
    }
});

const scrollableDiv = document.querySelector(
    '.pageWrapper .tweetsContainer .smallFormContentWrapper'
);

scrollableDiv.addEventListener('scroll', function () {
    if (
        Math.ceil(scrollableDiv.scrollTop + scrollableDiv.clientHeight) >=
            scrollableDiv.scrollHeight &&
        !contentIsLoading
    ) {
        const loader = document.createElement('div');
        loader.classList.add('loader');
        document
            .querySelector('.pageWrapper .tweetsContainer .smallFormContentWrapper')
            .appendChild(loader);
        createTweets();
        contentIsLoading = true;
    }
});
