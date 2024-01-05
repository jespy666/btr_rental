import vk_api


class VKBase:
    def __init__(self, access_token):
        self.access_token = access_token
        self.vk_session = vk_api.VkApi(token=access_token)
        self.vk = self.vk_session.get_api()


class TopicComments(VKBase):
    def __init__(self, group_id, topic_id, access_token):
        super().__init__(access_token)
        self.group_id = group_id
        self.topic_id = topic_id
        self.comments = {}

    def forming_comments(self) -> None:
        """Get raw comments from vk public"""
        self.comments = self.vk.board.getComments(
            group_id=self.group_id,
            topic_id=self.topic_id,
            extended=1
        )

    def get_formatted_comments(self) -> list:
        """Get comments ready to template built in"""
        comments = []
        for comment in self.comments['items'][1:]:
            user_id = comment['from_id']
            user_info = self.vk.users.get(user_ids=user_id,
                                          fields='photo_100')[0]
            comment_data = {
                'comment': comment,
                'user': user_info,
            }
            comments.append(comment_data)
        return comments

    def get_comments(self) -> list:
        self.forming_comments()
        return self.get_formatted_comments()


class SendBookingNotification(VKBase):

    def __init__(self, group_id, access_token):
        super().__init__(access_token)
        self.group_id = group_id

    def send_notify(self, message: str) -> None:
        self.vk.messages.send(
            user_id=self.group_id,
            message=message,
            random_id=0
        )
