import vk_api


def get_vk_comments(group_id, topic_id, access_token):
    vk_session = vk_api.VkApi(token=access_token)
    vk = vk_session.get_api()

    comments_info = vk.board.getComments(
        group_id=group_id,
        topic_id=topic_id,
        extended=1
    )

    comments = []
    for comment in comments_info['items'][1:]:
        user_id = comment['from_id']
        user_info = vk.users.get(user_ids=user_id, fields='photo_100')[0]

        comment_data = {
            'comment': comment,
            'user': user_info,
        }

        comments.append(comment_data)

    return comments
