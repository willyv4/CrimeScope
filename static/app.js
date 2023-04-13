async function createUserPost(placeUrl, title, content) {
  const resp = await axios.post(`/create/userpost`, {
    title: title,
    content: content,
    placeUrl: placeUrl,
  });

  postId = resp.data.post.id;
  await getUserPost(postId);
}

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

  const newPost = `<div class="p-4 border rounded-lg shadow-md">
          <h3 class="text-gray-600 mb-2">Created by: ${user.username}</h3>
          <h3 class="text-lg font-medium mb-2">${title}</h3>
          <p class="text-gray-600 mb-4">${content}</p>
          <p>${place.city} ${place.state}</p>
          <div class="flex items-center mb-2">
            <p "number-votes-${id}" class="text-gray-600">${num_votes}</p>
             <button type="submit" id="users-post"><svg
          stroke="currentColor"
          fill="currentColor"
          stroke-width="0"
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
          ></path></svg>
          </div>
        </div>`;
  $("#user-post-container").prepend(newPost);
}

async function postUpvote(data) {
  const resp = await axios.post("/post/upvote", data);
  const voteClass = resp.data[0]["class"];
  const message = resp.data[0]["message"];
  console.log(message);

  $("#vote-form-button").removeClass().addClass(voteClass);
  $("#flash-container").empty();
  $("#flash-container").append(message).fadeIn();
  if ($("#flash-container").length !== 0) {
    setTimeout(() => {
      $("#flash-container").fadeOut();
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

$("#create_post_for_city").on("submit", async function (e) {
  e.preventDefault();

  const title = $("#post-title").val();
  const content = $("#post-content").val();
  const placeUrl = $("#place-url").val();
  const city = $("#city_name").val();
  await createUserPost(placeUrl, title, content);
  $("#create_post_for_city")[0].reset();
});

$("#city-form").on("submit", async function (event) {
  const cityInput = $("#city-input").val();
  const stateInput = $("#state-input").val();
  console.log(cityInput);
  console.log(stateInput);
  await sendCityFormData(cityInput, stateInput);
});

async function fetchDataWithDelay() {
  const placeUrl = $("#place-url").val();
  const storageKey = `crimeData_${placeUrl}`;

  const storedData = localStorage.getItem(storageKey);

  if (storedData) {
    const parsedData = JSON.parse(storedData);
    $("#ai-response").append(`<p>${parsedData}</p>`);
  } else {
    const response = await axios.get("/get_crime_data");
    const responseData = response.data["data"];

    localStorage.setItem(storageKey, JSON.stringify(responseData));

    $("#ai-response").append(`<p>${responseData}</p>`);
  }
}

async function genNewResp() {
  const response = await axios.get("/get_crime_data");
  const responseData = response.data["data"];
  $("#ai-response").append(`<p>${responseData}</p>`);
}

$("#generate-ai-resp").click(function () {
  console.log("hello");

  // Remove the existing response
  $("#ai-response").empty();
  // Call the function again to regenerate the response
  genNewResp();
});

const placeUrl = $("#place-url").val();
if (
  (window.location.href.includes(placeUrl) && placeUrl !== null) ||
  undefined
) {
  fetchDataWithDelay();
}
