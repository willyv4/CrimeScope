/* 
 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
   CREATE USER POST AND HANDLE VOTE MESSAGE ON FRONT-END
 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

async function createUserPost(placeUrl, title, content) {
  const resp = await axios.post(`/create/userpost`, {
    title: title,
    content: content,
    placeUrl: placeUrl,
  });

  $("#flash-container").empty();
  $("#flash-container").append("Post created").fadeIn();
  if ($("#flash-container").length !== 0) {
    setTimeout(() => {
      $("#flash-container").fadeOut();
    }, 2000);
  }

  postId = resp.data.post.id;
  await getUserPost(postId);
}

$("#create_post_for_city").on("submit", async function (e) {
  e.preventDefault();

  const title = $("#post-title").val();
  const content = $("#post-content").val();
  const placeUrl = $("#place-url").val();
  const city = $("#city_name").val();
  await createUserPost(placeUrl, title, content);
  $("#create_post_for_city")[0].reset();
  $("#no-post-content").remove();
});

async function getUserPost(postId) {
  const response = await axios.get(`/${postId}`);

  const {
    id,
    title,
    content,
    place_city_url,
    user_id,
    created_at,
    place,
    user,
    num_votes,
  } = response.data.post;

  const newPost = `      
      <div class="border-2 border-gray-500 rounded shadow-lg bg-gray-50">
        <div class="p-4">
          <div class="flex justify-between">
            <h3 class="text-lg font-medium mb-4">${title}</h3>
            <span class="text-gray-600"
              >Created by: ${user.username}</span
            >
          </div>
          <p class="text-gray-600 bg-white mb-4 p-4 shadow-inner rounded">
            ${content}
          </p>
          <div class="flex bg-gray-100 p-1 rounded">
            <span class="w-11/12 mt-2 ml-2">
              ${place.city} ${place.state}
            </span>
            <p id="number-votes-${id}" class="text-gray-600 mt-2 w-4">
              ${num_votes}
            </p>
            <div id="div-vote-button" class="vote-form mt-2 ml-2 mr-2 w-4">
              <button
                id="vote-form-button"
                class="bg-gray-300 rounded"
              >
                <svg
                  stroke="currentColor"
                  fill="currentColor"
                  stroke-width=".5"
                  viewBox="0 0 16 16"
                  height="1.5em"
                  width="1.5em"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    fill-rule="evenodd"
                    d="M4 1h8a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V3a2 2 0 012-2zm0 1a1 1 0 00-1 1v10a1 1 0 001 1h8a1 1 0 001-1V3a1 1 0 00-1-1H4z"
                    clip-rule="evenodd"
                  ></path>
                  <path
                    fill-rule="evenodd"
                    d="M4.646 7.854a.5.5 0 00.708 0L8 5.207l2.646 2.647a.5.5 0 00.708-.708l-3-3a.5.5 0 00-.708 0l-3 3a.5.5 0 000 .708z"
                    clip-rule="evenodd"
                  ></path>
                  <path
                    fill-rule="evenodd"
                    d="M8 12a.5.5 0 00.5-.5v-6a.5.5 0 00-1 0v6a.5.5 0 00.5.5z"
                    clip-rule="evenodd"
                  ></path>
                </svg>
              </button>
              </div>
          </div>
        </div>
      </div>`;
  $("#user-post-container").prepend(newPost);

  $("#vote-form-button").on("click", () => {
    console.log("this should flash");
    $("#flash-container-js").empty();
    $("#flash-container-js").append("You can't vote on your post").fadeIn();
    if ($("#flash-container-js").length !== 0) {
      setTimeout(() => {
        $("#flash-container-js").fadeOut();
      }, 2000);
    }
  });
}

if ($("#flash-container").length !== 0) {
  setTimeout(() => {
    $("#flash-container").fadeOut();
  }, 3500);
}

/* 
 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  HANDLE VOTES  HANDLE VOTES  HANDLE VOTES 
 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

async function postUpvote(data) {
  const resp = await axios.post("/post/upvote", data);
  const voteClass = resp.data[0]["class"];
  const message = resp.data[0]["message"];
  const postId = resp.data[0]["post-id"];

  $(`#vote-form-button-${postId}`).removeClass().addClass(voteClass);
  $("#flash-container-js").empty();
  $("#flash-container-js").append(message).fadeIn();
  if ($("#flash-container-js").length !== 0) {
    setTimeout(() => {
      $("#flash-container-js").fadeOut();
    }, 2000);
  }
}

async function getUpvote(data) {
  const resp = await axios.get(`/get/upvote`, { params: data });
  $(`#number-votes-${data["postId"]}`).text(`${resp.data[0]["upvotes"]}`);
}

$(".vote-form").on("submit", async function (e) {
  e.preventDefault();

  const form = $(this).closest("form");
  const postId = form.find("input[name='vote-id']").val();

  await postUpvote({ postId: postId });
  await getUpvote({ postId: postId });
});

/* 
 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  HANLDE GPT AI RESPONSE AND STORE FIRST RESPONSE
  IN LOCAL STORAGE
 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

async function getAiResponse() {
  const placeUrl = $("#place-url").val();
  const storageKey = `crimeData_${placeUrl}`;

  const storedData = localStorage.getItem(storageKey);

  if (storedData) {
    const parsedData = JSON.parse(storedData);
    $("#ai-response").append(
      `<textarea readonly class="w-full h-full overflow-y-scroll p-6 focus:outline-none focus:shadow-outline resize-none">${parsedData}</textarea>`
    );
  } else {
    $("#ai-response").append(
      `<div id="loading-container" class="flex items-center justify-center w-full h-full"><i id="loading" class="fa fa-spinner fa-spin text-4xl"></i> <span class="ml-2">CrimeScope BOT is thinking...</span></div>`
    );

    const response = await axios.get("/generate_ai");
    const responseData = response.data["data"];

    localStorage.setItem(storageKey, JSON.stringify(responseData));

    $("#loading-container").remove();

    $("#ai-response").append(
      `<textarea readonly class="w-full h-full overflow-y-scroll p-6 focus:outline-none focus:shadow-outline resize-none">${responseData}</textarea>`
    );
  }
}

async function getNewAiResp() {
  const response = await axios.get("/generate_ai");
  const responseData = response.data["data"];

  if (responseData) {
    $("#loading-container").remove();
    $("#ai-response").append(
      `<textarea readonly class="w-full h-full overflow-y-scroll p-6 focus:outline-none focus:shadow-outline resize-none">${responseData}</textarea>`
    );
  }
}

$("#generate-ai-resp").click(function () {
  $("#ai-response").empty();

  $("#ai-response").append(
    `<div id="loading-container" class="flex items-center justify-center w-full h-full"><i id="loading" class="fa fa-spinner fa-spin text-4xl"></i> <span class="ml-2">CrimeScope BOT is thinking...</span></div>`
  );

  getNewAiResp();
});

const placeUrl = $("#place-url").val();
if (
  (window.location.href.includes(placeUrl) && placeUrl !== null) ||
  undefined
) {
  console.log("api called");
  getAiResponse();
}

/* 
 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  TOGGLE DELETE ACCOUNT BUTTON ON USER PROFILE
 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

$("#toggle-delete-visibility").on("click", () => {
  const delBtn = $("#account-delete-button");
  delBtn.removeClass("hidden");

  delBtn.on("click", () => {
    delBtn.addClass("hidden");
  });
});
