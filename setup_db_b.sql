
INSERT INTO "address" (address_id, house_name_number, street, town_city, county, country, postcode)
VALUES	(1, '1', 'Digital Street', 'Bristol', 'Bristol', 'England', 'BS2 8EN'),

		(2, '10', 'Digital Street', 'Bristol', 'Bristol', 'England', 'BS2 8EN'),
		(3, '11', 'Digital Street', 'Bristol', 'Bristol', 'England', 'BS2 8EN'),

		(4, '20', 'Digital Street', 'Bristol', 'Bristol', 'England', 'BS2 8EN'),
		(5, '21', 'Digital Street', 'Bristol', 'Bristol', 'England', 'BS2 8EN'),

		(6, '30', 'Digital Street', 'Bristol', 'Bristol', 'England', 'BS2 8EN'),
		(7, '31', 'Digital Street', 'Bristol', 'Bristol', 'England', 'BS2 8EN'),
		(8, '32', 'Digital Street', 'Bristol', 'Bristol', 'England', 'BS2 8EN');
ALTER SEQUENCE "address_address_id_seq" RESTART WITH 9;

INSERT INTO "user" (identity, first_name, last_name, email_address, phone_number, address_id)
VALUES	(1, 'Lisa', 'White', 'lisa.white@example.com', '07700900354', 2),
		(2, 'David', 'Jones', 'david.jones@example.com', '07700900827', 3),

		(3, 'Natasha', 'Powell', 'natasha.powell@example.com', '07700900027', 4),
		(4, 'Samuel', 'Barnes', 'samuel.barnes@example.com', '07700900534', 5),

		(5, 'Jim', 'Smith', 'jim.smith@example.com', '07700900815', 6),
		(6, 'Martin', 'Keats', 'martin.keats@example.com', '07700900133', 7),
		(7, 'Holly', 'Windsor', 'holly.windsor@example.com', '07700900970', 8);

INSERT INTO "case" (case_type, status, case_reference, created_at, title_number, assigned_staff_id, client_id, counterparty_id, counterparty_conveyancer_org, counterparty_conveyancer_contact_id, address_id)
VALUES	('buy', 'active', 'LAUN245', '2018-11-01 09:00:00.000000', 'ZQV888860', 4, 2, 1, 'O=Conveyancer1,L=Plymouth,C=GB', 3, 1),
		('buy', 'active', 'HETC016', '2018-11-01 09:00:00.000000', 'ZQV888861', 4, 2, 5, 'O=Conveyancer1,L=Plymouth,C=GB', 3, 6),
		('buy', 'active', 'JFYQ117', '2018-11-01 09:00:00.000000', 'ZQV888862', 4, 2, 6, 'O=Conveyancer1,L=Plymouth,C=GB', 3, 7),
		('sell', 'active', 'NATT237', '2018-11-01 09:00:00.000000', NULL, 4, 7, 2, 'O=Conveyancer1,L=Plymouth,C=GB', 3, 8),
		('buy', 'active', 'IIAS835', '2018-11-01 09:00:00.000000', 'RTV237231', 4, 7, 1, 'O=Conveyancer1,L=Plymouth,C=GB', 3, 2),
		('buy', 'active', 'PADV126', '2018-11-01 09:00:00.000000', 'RTV237232', 4, 6, 2, 'O=Conveyancer1,L=Plymouth,C=GB', 3, 3),
		('buy', 'active', 'LAXA531', '2018-11-01 09:00:00.000000', 'RTV237233', 2, 5, 3, 'O=Conveyancer1,L=Plymouth,C=GB', 1, 4),
		('sell', 'active', 'AHNI001', '2018-11-01 09:00:00.000000', NULL, 1, 4, 2, 'O=Conveyancer1,L=Plymouth,C=GB', 6, 5);
